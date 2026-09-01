"""
ml/network_features.py
Mule-to-Mule graph network construction and multi-hop feature extraction using NetworkX.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import networkx as nx


def build_case_graph(
    case_tx: pd.DataFrame,
    account_lookup: Optional[Dict[str, Dict[str, Any]]] = None
) -> nx.DiGraph:
    """
    Constructs a directed graph representing the mule network up to prediction time T.
    Nodes: Accounts (Victim / Mules)
    Edges: Directed transactions (sender -> receiver)
    """
    G = nx.DiGraph()

    if case_tx.empty:
        return G

    # Sort transactions chronologically
    sorted_tx = case_tx.sort_values("timestamp")

    for _, row in sorted_tx.iterrows():
        sender = str(row["sender_account"])
        receiver = str(row["receiver_account"])
        amt = float(row["amount"])
        ts = row["timestamp"]

        # Ensure node attributes are attached if lookup provided
        for acc in (sender, receiver):
            if not G.has_node(acc):
                acc_info = account_lookup.get(acc, {}) if account_lookup else {}
                G.add_node(
                    acc,
                    account_type=acc_info.get("account_type", "Mule" if "_1" not in acc else "Victim"),
                    region=acc_info.get("region", "Unknown"),
                    account_age_days=acc_info.get("account_age_days", 0)
                )

        G.add_edge(sender, receiver, amount=amt, timestamp=ts, transaction_id=row.get("transaction_id", ""))

    return G


def extract_network_features(
    case_tx: pd.DataFrame,
    account_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
    original_amount: float = 1.0
) -> Dict[str, float]:
    """
    Calculates graph-topological, multi-hop flow, and centrality features
    for a case using transactions observed strictly up to prediction time T.
    """
    default_features = {
        "network_num_accounts": 0.0,
        "network_num_mules": 0.0,
        "network_num_edges": 0.0,
        "terminal_in_degree": 0.0,
        "terminal_out_degree": 0.0,
        "terminal_total_degree": 0.0,
        "current_hop_number": 0.0,
        "max_hop_depth": 0.0,
        "num_downstream_accounts": 0.0,
        "num_upstream_accounts": 0.0,
        "num_mule_to_mule_transfers": 0.0,
        "total_amount_transferred_in_network": 0.0,
        "avg_transfer_delay_between_hops_min": 0.0,
        "amount_retained_ratio": 0.0,
        "pagerank_terminal": 0.0,
        "betweenness_terminal": 0.0,
    }

    if case_tx.empty:
        return default_features

    sorted_tx = case_tx.sort_values("timestamp")
    G = build_case_graph(sorted_tx, account_lookup)

    num_nodes = float(G.number_of_nodes())
    num_edges = float(G.number_of_edges())
    if num_nodes == 0:
        return default_features

    # Identify terminal node (the recipient of the latest transaction up to T)
    latest_tx = sorted_tx.iloc[-1]
    terminal_node = str(latest_tx["receiver_account"])

    # Identify victim node (in-degree == 0 and out-degree > 0, or account_type == 'Victim')
    victim_node = None
    for n, data in G.nodes(data=True):
        if data.get("account_type") == "Victim" or G.in_degree(n) == 0:
            victim_node = n
            break
    if victim_node is None:
        victim_node = str(sorted_tx.iloc[0]["sender_account"])

    # Node types
    num_mules = sum(1 for _, d in G.nodes(data=True) if d.get("account_type") == "Mule")

    # Degrees of terminal node
    term_in = float(G.in_degree(terminal_node)) if G.has_node(terminal_node) else 0.0
    term_out = float(G.out_degree(terminal_node)) if G.has_node(terminal_node) else 0.0
    term_tot = term_in + term_out

    # Multi-hop path distance from victim to terminal
    current_hop = 0.0
    if G.has_node(victim_node) and G.has_node(terminal_node):
        try:
            current_hop = float(nx.shortest_path_length(G, source=victim_node, target=terminal_node))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            current_hop = float(len(sorted_tx))

    # Maximum hop depth across all reachable paths from victim
    max_depth = current_hop
    if G.has_node(victim_node):
        try:
            lengths = nx.single_source_shortest_path_length(G, victim_node)
            if lengths:
                max_depth = float(max(lengths.values()))
        except Exception:
            max_depth = current_hop

    # Upstream and downstream connectivity
    downstream_cnt = 0.0
    upstream_cnt = 0.0
    if G.has_node(terminal_node):
        try:
            downstream_cnt = float(len(nx.descendants(G, terminal_node)))
            upstream_cnt = float(len(nx.ancestors(G, terminal_node)))
        except Exception:
            pass

    # Mule-to-mule count & total volume
    mule_to_mule_cnt = 0.0
    total_volume = 0.0
    for u, v, data in G.edges(data=True):
        total_volume += data.get("amount", 0.0)
        u_type = G.nodes[u].get("account_type")
        v_type = G.nodes[v].get("account_type")
        if u_type == "Mule" and v_type == "Mule":
            mule_to_mule_cnt += 1.0

    # Delay between successive transfers
    if len(sorted_tx) > 1:
        time_diffs = sorted_tx["timestamp"].diff().dropna().dt.total_seconds() / 60.0
        avg_delay = float(time_diffs.mean())
    else:
        avg_delay = 0.0

    # Amount retained ratio
    terminal_amt = float(latest_tx["amount"])
    ref_amt = original_amount if original_amount > 0 else 1.0
    retained_ratio = terminal_amt / ref_amt

    # Centralities
    try:
        pr = nx.pagerank(G, weight="amount")
        pr_val = float(pr.get(terminal_node, 0.0))
    except Exception:
        pr_val = 1.0 / num_nodes if num_nodes > 0 else 0.0

    try:
        bc = nx.betweenness_centrality(G)
        bc_val = float(bc.get(terminal_node, 0.0))
    except Exception:
        bc_val = 0.0

    return {
        "network_num_accounts": num_nodes,
        "network_num_mules": float(num_mules),
        "network_num_edges": num_edges,
        "terminal_in_degree": term_in,
        "terminal_out_degree": term_out,
        "terminal_total_degree": term_tot,
        "current_hop_number": current_hop,
        "max_hop_depth": max_depth,
        "num_downstream_accounts": downstream_cnt,
        "num_upstream_accounts": upstream_cnt,
        "num_mule_to_mule_transfers": mule_to_mule_cnt,
        "total_amount_transferred_in_network": total_volume,
        "avg_transfer_delay_between_hops_min": avg_delay,
        "amount_retained_ratio": retained_ratio,
        "pagerank_terminal": pr_val,
        "betweenness_terminal": bc_val,
    }


if __name__ == "__main__":
    from ml.data_loader import load_raw_data
    from ml.preprocessing import build_account_lookup

    cases, accs, txs, locs, withs = load_raw_data()
    acc_map = build_account_lookup(accs)
    c1_tx = txs[txs["case_id"] == "C0001"]
    net_feats = extract_network_features(c1_tx, acc_map, original_amount=148790)
    print("[STEP 2 SUCCESS] Case C0001 network features:")
    for k, v in net_feats.items():
        print(f"  {k}: {v}")
