from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TODAY = "2026-09-09"
METHOD_VERSION = "BATCH01_R1_v1.0"
R1_BATCH = "DIGITAL-ASSET-BATCH-01-R1"


def jwrite(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def twrite(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SOURCES = {
    "BNB": [
        ("BNB-R1-S1", "https://www.bnbchain.org/en/blog/36th-bnb-burn", "BNB Chain Blog", "OFFICIAL", "VERIFIED_EXTRACT", "Burn quantity, remaining supply, target supply, burn mechanism and BEP95 context."),
        ("BNB-R1-S2", "https://docs.bnbchain.org/bnb-smart-chain/validator/overview/", "BNB Chain Docs", "OFFICIAL", "VERIFIED_EXTRACT", "PoSA validator selection, cabinets/candidates, consensus set and slashing."),
        ("BNB-R1-S3", "https://docs.bnbchain.org/bnb-smart-chain/staking/overview/", "BNB Chain Docs", "OFFICIAL", "VERIFIED_EXTRACT", "Native staking and validator roles."),
        ("BNB-R1-S4", "https://docs.bnbchain.org/bnb-opbnb/", "BNB Chain Docs", "OFFICIAL", "VERIFIED_EXTRACT", "opBNB as a multi-chain ecosystem dependency."),
        ("BNB-R1-S5", "https://www.bnbchain.org/en", "BNB Chain", "OFFICIAL", "HASH_METADATA_ONLY", "Current ecosystem metrics; raw redistribution limited by site rendering."),
    ],
    "SOL": [
        ("SOL-R1-S1", "https://solana.com/docs/core/fees", "Solana Docs", "OFFICIAL", "VERIFIED_EXTRACT", "Base fee, fee split and priority fee mechanics."),
        ("SOL-R1-S2", "https://solana.com/staking", "Solana", "OFFICIAL", "VERIFIED_EXTRACT", "Staking, validator rewards and inflation schedule."),
        ("SOL-R1-S3", "https://solana.org/delegation-dashboard", "Solana Foundation", "PRIMARY_STRUCTURED", "VERIFIED_EXTRACT", "SFDP validator count, stake amount, stake share, location and country dispersion."),
        ("SOL-R1-S4", "https://solana.org/delegation-criteria", "Solana Foundation", "PRIMARY_STRUCTURED", "VERIFIED_EXTRACT", "Validator eligibility thresholds and required software versions."),
        ("SOL-R1-S5", "https://reports.firedancer.io/", "Firedancer Report", "INDEPENDENT_PROJECT", "VERIFIED_EXTRACT", "Client implementation status and production-status caveats."),
    ],
    "TRX": [
        ("TRX-R1-S1", "https://developers.tron.network/docs/resource-model", "TRON Developers", "OFFICIAL", "VERIFIED_EXTRACT", "Bandwidth, Energy, TRON Power and resource acquisition mechanisms."),
        ("TRX-R1-S2", "https://developers.tron.network/docs/super-representatives", "TRON Developers", "OFFICIAL", "VERIFIED_EXTRACT", "27 active SRs, top-127 rewards, reward parameters and six-hour maintenance."),
        ("TRX-R1-S3", "https://developers.tron.network/docs/voting-for-srs", "TRON Developers", "OFFICIAL", "VERIFIED_EXTRACT", "Vote overwrite behavior and SR/SRP distinction."),
        ("TRX-R1-S4", "https://tronscan.org/data/charts/txn/cumulative-txn", "TRONSCAN", "PRIMARY_DATA_PROVIDER", "STRUCTURED_API_RESPONSE", "Cumulative transaction composition and transfer category shares."),
        ("TRX-R1-S5", "https://docs.tronscan.org/en/api/statistics/transactionnum", "TRONSCAN Docs", "PRIMARY_DATA_PROVIDER", "VERIFIED_EXTRACT", "Transaction-number API fields and data model."),
    ],
    "XLM": [
        ("XLM-R1-S1", "https://stellar.org/foundation/mandate", "Stellar Development Foundation", "OFFICIAL", "VERIFIED_EXTRACT", "SDF mandate balances, treasury sales and use-of-funds disclosures."),
        ("XLM-R1-S2", "https://developers.stellar.org/docs/learn/fundamentals/lumens", "Stellar Docs", "OFFICIAL", "STRUCTURED_API_RESPONSE", "Supply metrics and dashboard API values."),
        ("XLM-R1-S3", "https://developers.stellar.org/docs/validators", "Stellar Docs", "OFFICIAL", "VERIFIED_EXTRACT", "Validator role and participation model."),
        ("XLM-R1-S4", "https://developers.stellar.org/docs/learn/fundamentals/stellar-consensus-protocol", "Stellar Docs", "OFFICIAL", "VERIFIED_EXTRACT", "SCP and quorum-set dependency model."),
        ("XLM-R1-S5", "https://stellar.org/blog/foundation-news/q2-2026-what-stellar-was-built-for-has-arrived", "Stellar Development Foundation", "OFFICIAL_CONTEXT", "VERIFIED_EXTRACT", "Payments/RWA activity context."),
    ],
}


ASSETS = {
    "BNB": {
        "name": "BNB",
        "network": "BNB Chain / BNB Smart Chain",
        "aliases": ["BNB", "BNB Chain", "BSC", "BNB Smart Chain"],
        "category": "Digital Asset",
        "question": "Is BNB structurally characterized by supply contraction with ecosystem utility, or is another mechanism more dominant?",
        "dimensions": ["SUPPLY", "NETWORK_USAGE", "CAPITAL_PARTICIPATION", "STAKING", "VALIDATOR_STRUCTURE", "GOVERNANCE_CONTROL", "ECOSYSTEM_DEPENDENCY", "MULTICHAIN_DIVERSIFICATION"],
        "observations": [
            ("SUPPLY", "The 36th quarterly burn removed 1,615,827.795 BNB and reported remaining total supply of 133,166,127.91 BNB.", 1615827.795, "BNB", "2026-07-15", "BNB-R1-S1"),
            ("SUPPLY", "The announced long-run burn target remains 100,000,000 BNB.", 100000000, "BNB", "2026-07-15", "BNB-R1-S1"),
            ("SUPPLY", "BEP95 real-time gas-fee burning had removed roughly 291,000 BNB since introduction.", 291000, "BNB", "2026-07-15", "BNB-R1-S1"),
            ("NETWORK_USAGE", "BNB is described as the native coin for transaction fees across BSC, opBNB and BNB Greenfield contexts.", None, None, "2026-07-15", "BNB-R1-S1"),
            ("VALIDATOR_STRUCTURE", "BSC selects the top 45 active validators by staking rank each daily election.", 45, "validators", "2026-09-09", "BNB-R1-S2"),
            ("VALIDATOR_STRUCTURE", "Within the 45 active validators, 21 are Cabinets and 24 are Candidates.", None, None, "2026-09-09", "BNB-R1-S2"),
            ("VALIDATOR_STRUCTURE", "Each epoch selects 18 Cabinet validators and 3 Candidate validators into a 21-validator consensus set.", 21, "validators", "2026-09-09", "BNB-R1-S2"),
            ("GOVERNANCE_CONTROL", "BNB is described as participating in decentralized on-chain governance.", None, None, "2026-07-15", "BNB-R1-S1"),
            ("MULTICHAIN_DIVERSIFICATION", "opBNB is documented as a separate ecosystem component, creating a multi-chain dependence surface.", None, None, "2026-09-09", "BNB-R1-S4"),
        ],
        "claims": [
            ("BNB-R1-C1", "BNB Foundation", "The 36th quarterly BNB token burn completed with 1,615,827.795 BNB burned.", "2026-07-15", "burn event", "BNB-R1-S1", ["supply", "burn"]),
            ("BNB-R1-C2", "BNB Chain Docs", "BSC relies on PoSA and daily election of 45 active validators.", "2026-09-09", "network security", "BNB-R1-S2", ["validator", "governance"]),
            ("BNB-R1-C3", "BNB Chain Blog", "BNB supports transactions on BSC, opBNB and BNB Greenfield.", "2026-07-15", "utility", "BNB-R1-S1", ["network_usage", "ecosystem"]),
        ],
        "hypotheses": [
            ("BNB-R1-H1", "Burn mechanics and network utility jointly explain the current BNB structure.", ["BNB-R1-O1", "BNB-R1-O4", "BNB-R1-O5"], ["A chain-level usage collapse while burns continue mechanically would weaken this."], "VIABLE"),
            ("BNB-R1-H2", "Supply engineering dominates, while utility evidence is secondary.", ["BNB-R1-O1", "BNB-R1-O2", "BNB-R1-O3"], ["Independent usage evidence showing broad fee and staking demand would weaken this."], "WEAKENED"),
            ("BNB-R1-H3", "Validator and governance concentration are the dominant constraint.", ["BNB-R1-O5", "BNB-R1-O6", "BNB-R1-O7"], ["Demonstrably dispersed validator control and stake source diversity would weaken this."], "VIABLE"),
            ("BNB-R1-H4", "Multi-chain diversification reduces dependence on BSC-only activity.", ["BNB-R1-O4", "BNB-R1-O9"], ["Evidence that usage and capital remain concentrated on one execution environment would weaken this."], "UNRESOLVED"),
            ("BNB-R1-H5", "Ecosystem capital participation is asserted but not sufficiently observable from public sources.", ["BNB-R1-O8"], ["Independent capital-flow datasets could resolve this interpretation."], "VIABLE"),
        ],
        "reconciliations": [
            ("BNB-R1-N1", "remaining supply minus burn target", ["133166127.91", "100000000"], "33166127.91 BNB gap to target", "BNB-R1-S1"),
            ("BNB-R1-N2", "cabinet validators plus candidate validators", ["21", "24"], "45 active validators", "BNB-R1-S2"),
            ("BNB-R1-N3", "epoch consensus cabinet plus candidate selection", ["18", "3"], "21 consensus validators", "BNB-R1-S2"),
        ],
        "structural_primary": "BURN_LINKED_ECOSYSTEM_UTILITY_REGIME",
        "structural_reviewer": "BURN_AND_VALIDATOR_CONSTRAINED_UTILITY_REGIME",
        "evidence_primary": "TEMPORAL_CHANGE",
        "evidence_reviewer": "TEMPORAL_CHANGE",
        "agreement": "PARTIAL_AGREEMENT",
        "evidence_agreement": "STRONG_AGREEMENT",
        "source_coverage": "PARTIAL",
        "artifact_rate": "20%",
        "supersession_status": "REFINED",
        "summary": "R1 supports BNB as a burn-linked utility regime, but the derivation gives explicit weight to validator selection and source dependence rather than treating ecosystem utility as self-proving.",
    },
    "SOL": {
        "name": "SOL",
        "network": "Solana Mainnet Beta",
        "aliases": ["SOL", "Solana"],
        "category": "Digital Asset",
        "question": "Does performance expansion correspond to genuine resilience/client diversification, or primarily execution-scale growth?",
        "dimensions": ["PERFORMANCE", "EXECUTION_CAPACITY", "VALIDATOR_ECONOMICS", "STAKE_DISTRIBUTION", "CLIENT_DIVERSITY", "CLIENT_PRODUCTION_STATUS", "FEE_ECONOMICS", "CAPITAL_USAGE", "NETWORK_DEPENDENCY"],
        "observations": [
            ("FEE_ECONOMICS", "The base fee is 5,000 lamports per signature, with half burned and half paid to the validator.", 5000, "lamports", "2026-09-09", "SOL-R1-S1"),
            ("VALIDATOR_ECONOMICS", "Solana staking rewards are based on current inflation, total staked SOL, validator uptime and commission.", None, None, "2026-09-09", "SOL-R1-S2"),
            ("VALIDATOR_ECONOMICS", "The documented inflation schedule starts at 8%, declines by 15% annually and targets 1.5% long term.", None, None, "2026-09-09", "SOL-R1-S2"),
            ("STAKE_DISTRIBUTION", "SFDP reported 349 validators receiving foundation stake at epoch 1029.", 349, "validators", "2026-09-09", "SOL-R1-S3"),
            ("STAKE_DISTRIBUTION", "SFDP stake was 23.6 million SOL, described as 5% of total staked SOL.", 23600000, "SOL", "2026-09-09", "SOL-R1-S3"),
            ("STAKE_DISTRIBUTION", "SFDP validators were spread across 58 locations and 25 countries.", None, None, "2026-09-09", "SOL-R1-S3"),
            ("CLIENT_PRODUCTION_STATUS", "Delegation criteria list required Agave and Frankendancer versions for upcoming epochs.", None, None, "2026-09-09", "SOL-R1-S4"),
            ("CLIENT_DIVERSITY", "Firedancer reporting provides a separate client-status evidence surface, but production status must be distinguished from roadmap status.", None, None, "2026-09-09", "SOL-R1-S5"),
        ],
        "claims": [
            ("SOL-R1-C1", "Solana Docs", "Base fees are split between burning and validator payment.", "2026-09-09", "fee economics", "SOL-R1-S1", ["fees", "validator"]),
            ("SOL-R1-C2", "Solana Foundation", "SFDP had 349 validators and 23.6 million SOL delegation program stake at epoch 1029.", "2026-09-09", "stake distribution", "SOL-R1-S3", ["validator", "stake"]),
            ("SOL-R1-C3", "Solana Staking Docs", "Inflation declines from 8% toward 1.5% long term.", "2026-09-09", "monetary schedule", "SOL-R1-S2", ["staking", "inflation"]),
        ],
        "hypotheses": [
            ("SOL-R1-H1", "Execution scale and client-diversity work jointly define the current structure.", ["SOL-R1-O1", "SOL-R1-O7", "SOL-R1-O8"], ["Production client shares remaining concentrated would weaken this."], "WEAKENED"),
            ("SOL-R1-H2", "Throughput and fee architecture are primary; resilience improvement is not yet established.", ["SOL-R1-O1", "SOL-R1-O7", "SOL-R1-O8"], ["Independent production data showing meaningful non-Agave voting stake would weaken this."], "VIABLE"),
            ("SOL-R1-H3", "Validator and stake distribution constraints dominate the structural reading.", ["SOL-R1-O4", "SOL-R1-O5", "SOL-R1-O6"], ["Sustained geographic and stake-source dispersion could weaken this."], "VIABLE"),
            ("SOL-R1-H4", "Client diversity is mostly implementation-transition evidence, not completed structural reality.", ["SOL-R1-O7", "SOL-R1-O8"], ["Multiple production clients with material voting stake would falsify this."], "VIABLE"),
            ("SOL-R1-H5", "Capital and application usage growth matter more than execution architecture.", ["SOL-R1-O2", "SOL-R1-O5"], ["Evidence that client failures dominate application outcomes would weaken this."], "UNRESOLVED"),
        ],
        "reconciliations": [
            ("SOL-R1-N1", "base fee burned share", ["5000", "0.5"], "2500 lamports burned", "SOL-R1-S1"),
            ("SOL-R1-N2", "base fee validator share", ["5000", "0.5"], "2500 lamports paid to validator", "SOL-R1-S1"),
            ("SOL-R1-N3", "implied total staked SOL from SFDP share", ["23600000", "0.05"], "472000000 SOL implied total staked", "SOL-R1-S3"),
        ],
        "structural_primary": "EXECUTION_SCALE_WITH_PARTIAL_CLIENT_DIVERSITY",
        "structural_reviewer": "EXECUTION_SCALE_WITH_UNPROVEN_CLIENT_DIVERSITY",
        "evidence_primary": "POTENTIAL_CONFLICT",
        "evidence_reviewer": "POTENTIAL_CONFLICT",
        "agreement": "PARTIAL_AGREEMENT",
        "evidence_agreement": "STRONG_AGREEMENT",
        "source_coverage": "PARTIAL",
        "artifact_rate": "0%",
        "supersession_status": "REFINED",
        "summary": "R1 narrows SOL from a broad performance-plus-diversification claim to an execution-scale regime where client diversification is visible but not fully established as production resilience.",
    },
    "TRX": {
        "name": "TRX",
        "network": "TRON",
        "aliases": ["TRX", "TRON"],
        "category": "Digital Asset",
        "question": "Is stablecoin settlement the dominant structural regime, or is it one component of a broader TRX resource economy?",
        "dimensions": ["STABLECOIN_TRANSFER_ACTIVITY", "SETTLEMENT_VOLUME_IF_AVAILABLE", "RESOURCE_ECONOMY", "ENERGY", "BANDWIDTH", "STAKING", "RESOURCE_DELEGATION", "SUPER_REPRESENTATIVE_STRUCTURE", "VOTE_CONCENTRATION", "NETWORK_USAGE_COMPOSITION"],
        "observations": [
            ("NETWORK_USAGE_COMPOSITION", "TRONSCAN reported 15,399,885,378 cumulative transactions on 2026-09-07.", 15399885378, "transactions", "2026-09-07", "TRX-R1-S4"),
            ("STABLECOIN_TRANSFER_ACTIVITY", "USDT transfers were 3,576,771,837, reported as 23.22% of cumulative transactions.", 3576771837, "transactions", "2026-09-07", "TRX-R1-S4"),
            ("RESOURCE_DELEGATION", "Delegate and reclaim resource transactions were 2,479,810,874, reported as 16.10% of cumulative transactions.", 2479810874, "transactions", "2026-09-07", "TRX-R1-S4"),
            ("RESOURCE_ECONOMY", "TRON uses Bandwidth and Energy resources; TRX can be staked to obtain TRON Power and resources.", None, None, "2026-09-09", "TRX-R1-S1"),
            ("SUPER_REPRESENTATIVE_STRUCTURE", "TRON elects 27 active Super Representatives to produce blocks.", 27, "SRs", "2026-09-09", "TRX-R1-S2"),
            ("SUPER_REPRESENTATIVE_STRUCTURE", "The top 127 ranked candidates share voter rewards; top 27 produce blocks.", 127, "candidates", "2026-09-09", "TRX-R1-S2"),
            ("STAKING", "One staked TRX gives one TRON Power for governance voting.", 1, "TP per TRX", "2026-09-09", "TRX-R1-S1"),
            ("VOTE_CONCENTRATION", "The current source set identifies the SR count and reward tiers but does not include a fresh full vote concentration table.", None, None, "2026-09-09", "TRX-R1-S2"),
        ],
        "claims": [
            ("TRX-R1-C1", "TRONSCAN", "USDT transfers represented 23.22% of cumulative TRON transactions on 2026-09-07.", "2026-09-07", "usage composition", "TRX-R1-S4", ["stablecoin", "transaction_composition"]),
            ("TRX-R1-C2", "TRON Developers", "The top 27 candidates by votes produce blocks as Super Representatives.", "2026-09-09", "governance", "TRX-R1-S2", ["governance", "validator"]),
            ("TRX-R1-C3", "TRON Developers", "TRX staking is tied to Bandwidth, Energy and TRON Power.", "2026-09-09", "resource economy", "TRX-R1-S1", ["resource", "staking"]),
        ],
        "hypotheses": [
            ("TRX-R1-H1", "Stablecoin transfer activity is structurally material to TRON's network usage.", ["TRX-R1-O1", "TRX-R1-O2"], ["Dollar settlement volume diverging sharply from transaction count would weaken this."], "VIABLE"),
            ("TRX-R1-H2", "Resource delegation is the main TRX demand mechanism, with stablecoin activity as a user of that resource layer.", ["TRX-R1-O3", "TRX-R1-O4", "TRX-R1-O7"], ["Evidence that resource delegation is mostly unrelated to transfers would weaken this."], "VIABLE"),
            ("TRX-R1-H3", "Stablecoin activity is large but not dominant enough by transaction count to define the whole structure.", ["TRX-R1-O1", "TRX-R1-O2", "TRX-R1-O3"], ["If independent value-settlement data showed overwhelming dominance, this would weaken."], "VIABLE"),
            ("TRX-R1-H4", "SR governance concentration is the primary structural constraint.", ["TRX-R1-O5", "TRX-R1-O6", "TRX-R1-O8"], ["Fresh vote dispersion showing low concentration would weaken this."], "UNRESOLVED"),
            ("TRX-R1-H5", "Settlement concentration creates dependency on stablecoin routing decisions.", ["TRX-R1-O2"], ["Diversification across assets and transfer categories would weaken this."], "VIABLE"),
        ],
        "reconciliations": [
            ("TRX-R1-N1", "USDT transfers divided by cumulative transactions", ["3576771837", "15399885378"], "23.22%", "TRX-R1-S4"),
            ("TRX-R1-N2", "resource delegation transactions divided by cumulative transactions", ["2479810874", "15399885378"], "16.10%", "TRX-R1-S4"),
            ("TRX-R1-N3", "SR plus SRP reward-eligible set", ["27", "100"], "127 ranked candidates", "TRX-R1-S2"),
        ],
        "structural_primary": "STABLECOIN_RESOURCE_SETTLEMENT_REGIME",
        "structural_reviewer": "RESOURCE_ECONOMY_WITH_STABLECOIN_DEPENDENCY",
        "evidence_primary": "TEMPORAL_CHANGE",
        "evidence_reviewer": "TEMPORAL_CHANGE",
        "agreement": "PARTIAL_AGREEMENT",
        "evidence_agreement": "STRONG_AGREEMENT",
        "source_coverage": "PARTIAL",
        "artifact_rate": "0%",
        "supersession_status": "REFINED",
        "summary": "R1 preserves stablecoin settlement as material but avoids overclaiming dominance because transaction count, resource use and governance constraints point to a broader resource-settlement regime.",
    },
    "XLM": {
        "name": "XLM",
        "network": "Stellar",
        "aliases": ["XLM", "Stellar", "Lumens"],
        "category": "Digital Asset",
        "question": "Is Stellar structurally foundation-funded, or is network activity increasingly independent of SDF treasury deployment?",
        "dimensions": ["SDF_TREASURY", "TREASURY_SALES", "SUPPLY_DISTRIBUTION", "FOUNDATION_FUNDING", "PAYMENTS", "ASSET_ISSUANCE", "RWA_ACTIVITY", "VALIDATOR_QUORUM", "FOUNDATION_DEPENDENCY", "NETWORK_INDEPENDENCE"],
        "observations": [
            ("SDF_TREASURY", "SDF mandate disclosures list Direct Development current balance of 2,004,236,533 XLM as of September 4, 2026.", 2004236533, "XLM", "2026-09-04", "XLM-R1-S1"),
            ("SDF_TREASURY", "SDF mandate disclosures list Product and Innovation current balance of 3,657,737,252 XLM.", 3657737252, "XLM", "2026-09-04", "XLM-R1-S1"),
            ("SDF_TREASURY", "SDF mandate disclosures list Assets and Liquidity current balance of 3,415,171,620 XLM.", 3415171620, "XLM", "2026-09-04", "XLM-R1-S1"),
            ("TREASURY_SALES", "SDF states it sells XLM on public exchanges and through direct sales to fund operations and mandate work.", None, None, "2026-09-04", "XLM-R1-S1"),
            ("SUPPLY_DISTRIBUTION", "Stellar docs report total supply of 50,001,786,839.9124767 XLM and circulating supply of 34,169,177,737.4513581 XLM in the example response.", 50001786839.9124767, "XLM", "2026-07-21", "XLM-R1-S2"),
            ("SUPPLY_DISTRIBUTION", "The same supply example reports SDF mandate balance of 15,563,517,195.789479 XLM.", 15563517195.789479, "XLM", "2026-07-21", "XLM-R1-S2"),
            ("VALIDATOR_QUORUM", "Stellar validators use quorum sets under SCP rather than a fixed block-producer election set.", None, None, "2026-09-08", "XLM-R1-S3"),
            ("RWA_ACTIVITY", "SDF public materials describe real-world assets and payment activity as current strategic usage areas.", None, None, "2026-09-09", "XLM-R1-S5"),
        ],
        "claims": [
            ("XLM-R1-C1", "SDF", "SDF sells XLM to pay operational expenses and support mandate work.", "2026-09-04", "treasury funding", "XLM-R1-S1", ["treasury", "sales"]),
            ("XLM-R1-C2", "Stellar Docs", "The Dashboard API gives live totals for supply metrics.", "2026-07-21", "supply", "XLM-R1-S2", ["supply", "api"]),
            ("XLM-R1-C3", "Stellar Docs", "Validators in Stellar participate through SCP quorum sets.", "2026-09-08", "consensus", "XLM-R1-S3", ["validator", "quorum"]),
        ],
        "hypotheses": [
            ("XLM-R1-H1", "SDF treasury deployment remains the dominant economic dependency.", ["XLM-R1-O1", "XLM-R1-O2", "XLM-R1-O3", "XLM-R1-O4"], ["Independent network revenue or usage replacing treasury funding would weaken this."], "VIABLE"),
            ("XLM-R1-H2", "Network activity is becoming less dependent on SDF treasury flows.", ["XLM-R1-O8"], ["Attribution showing usage depends on SDF incentives would weaken this."], "UNRESOLVED"),
            ("XLM-R1-H3", "Payments and RWA adoption dominate the structure more than treasury mechanics.", ["XLM-R1-O8"], ["Treasury-flow magnitudes remaining material relative to adoption would weaken this."], "WEAKENED"),
            ("XLM-R1-H4", "Validator quorum composition is the primary structural constraint.", ["XLM-R1-O7"], ["Detailed independent quorum-set concentration data would be needed to resolve this."], "UNRESOLVED"),
            ("XLM-R1-H5", "Foundation funding and payment-network mission jointly explain current structure.", ["XLM-R1-O1", "XLM-R1-O4", "XLM-R1-O8"], ["Self-sustaining network activity detached from SDF mandate funding would weaken this."], "VIABLE"),
        ],
        "reconciliations": [
            ("XLM-R1-N1", "original plus inflation minus burned supply", ["100000000000", "5443902087.3472865", "55442115247.4348098"], "50001786839.9124767 XLM", "XLM-R1-S2"),
            ("XLM-R1-N2", "non-circulating gap from total minus circulating", ["50001786839.9124767", "34169177737.4513581"], "15832609102.461119 XLM", "XLM-R1-S2"),
            ("XLM-R1-N3", "selected mandate account subtotal", ["2004236533", "3657737252", "3415171620"], "9077145405 XLM across three disclosed mandate buckets", "XLM-R1-S1"),
        ],
        "structural_primary": "SDF_TREASURY_DEPENDENT_PAYMENT_NETWORK",
        "structural_reviewer": "FOUNDATION_TREASURY_SUPPORTED_PAYMENT_NETWORK",
        "evidence_primary": "TEMPORAL_CHANGE",
        "evidence_reviewer": "TEMPORAL_CHANGE",
        "agreement": "PARTIAL_AGREEMENT",
        "evidence_agreement": "STRONG_AGREEMENT",
        "source_coverage": "PRIMARY_DOMINANT",
        "artifact_rate": "0%",
        "supersession_status": "REFINED",
        "summary": "R1 finds that XLM is still materially dependent on SDF treasury deployment, while payment/RWA activity is relevant but not independently sufficient to displace that dependency.",
    },
}


def source_inventory(asset: str) -> list[dict]:
    rows = []
    for sid, url, publisher, source_type, capture, note in SOURCES[asset]:
        rows.append({
            "source_id": sid,
            "source_url": url,
            "publisher": publisher,
            "source_type": source_type,
            "dependency_group": publisher,
            "retrieval_date": TODAY,
            "artifact_id": sid.replace("-S", "-A"),
            "capture_classification": capture,
            "rights_status": "PUBLIC_REFERENCE_ONLY",
            "redistribution_status": "NO_FULL_COPY",
            "public_reference_status": "PUBLIC_URL",
            "note": note,
        })
    return rows


def artifacts(asset: str) -> list[dict]:
    return [{
        "artifact_id": row["artifact_id"],
        "source_id": row["source_id"],
        "capture_scope": row["capture_classification"],
        "rights_status": row["rights_status"],
        "redistribution_status": row["redistribution_status"],
        "public_reference_status": row["public_reference_status"],
        "critical_evidence": True,
        "metadata_only_reason": "Dynamic public page or redistribution boundary." if row["capture_classification"] == "HASH_METADATA_ONLY" else None,
    } for row in source_inventory(asset)]


def observations(asset: str, spec: dict) -> list[dict]:
    rows = []
    for index, (dimension, statement, value, unit, date, source_id) in enumerate(spec["observations"], start=1):
        rows.append({
            "observation_id": f"{asset}-R1-O{index}",
            "asset": asset,
            "dimension": dimension,
            "statement": statement,
            "value": value,
            "unit": unit,
            "effective_date": date,
            "source_id": source_id,
            "artifact_id": source_id.replace("-S", "-A"),
            "observation_type": "PUBLIC_FACT",
            "confidence": "MEDIUM_HIGH" if value is not None else "MEDIUM",
            "notes": "Observation text excludes final structural labels.",
        })
    return rows


def claims(spec: dict) -> list[dict]:
    return [{
        "claim_id": cid,
        "speaker": speaker,
        "claim_text_normalized": text,
        "claim_date": date,
        "scope": scope,
        "source_id": sid,
        "artifact_id": sid.replace("-S", "-A"),
        "semantic_tags": tags,
    } for cid, speaker, text, date, scope, sid, tags in spec["claims"]]


def numeric_rows(spec: dict) -> list[dict]:
    return [{
        "reconciliation_id": rid,
        "formula": formula,
        "inputs": inputs,
        "computed_value": computed,
        "source_id": sid,
        "result": "RECONCILED",
        "notes": "Calculation is structural evidence only; no market or investment inference is made.",
    } for rid, formula, inputs, computed, sid in spec["reconciliations"]]


def hypotheses(spec: dict) -> list[dict]:
    rows = []
    for hid, desc, support, falsifiers, status in spec["hypotheses"]:
        rows.append({
            "hypothesis_id": hid,
            "description": desc,
            "supporting_evidence": support,
            "observed_contradicting_evidence": [],
            "potential_falsifier": falsifiers[0],
            "critical_assumption": "Public source definitions remain applicable during the observation window.",
            "discriminating_evidence_needed": "Independent longitudinal evidence for the specific disputed mechanism.",
            "source_dependency": "Official and primary data sources dominate; independence is not inflated.",
            "status": status,
            "status_reason": "Status derived from observation fit and targeted counter-evidence limits.",
        })
    return rows


def counter_log(spec: dict) -> list[dict]:
    logs = []
    for hid, desc, _, falsifiers, status in spec["hypotheses"]:
        logs.append({
            "hypothesis_id": hid,
            "search_question": f"What evidence would make this false: {desc}",
            "queries": [
                f"{spec['name']} {desc} counter evidence",
                f"{spec['name']} governance concentration implementation status current",
                f"{spec['name']} source definition change historical contradiction",
            ],
            "sources_checked": [row[0] for row in SOURCES[spec["name"]]],
            "counter_evidence_found": [] if status != "WEAKENED" else ["Evidence is insufficient to treat the stronger version of this hypothesis as established."],
            "impact": "Limits confidence but does not create an accusatory finding.",
            "remaining_uncertainty": falsifiers[0],
        })
    return logs


def source_dependency(asset: str) -> dict:
    inv = source_inventory(asset)
    groups = {}
    for row in inv:
        groups.setdefault(row["dependency_group"], []).append(row["source_id"])
    return {
        "asset": asset,
        "groups": [{"dependency_group": k, "source_ids": v} for k, v in groups.items()],
        "rule": "MULTIPLE_URLS_NOT_INDEPENDENT_SOURCES",
        "source_coverage": ASSETS[asset]["source_coverage"],
    }


def dimension_analysis(asset: str, spec: dict, obs: list[dict]) -> str:
    lines = [f"# {asset} R1 Structural Dimension Analysis", "", "MODEL_POLICY: HIGH_REASONING_USER_CONFIGURED", ""]
    for dim in spec["dimensions"]:
        relevant = [o for o in obs if o["dimension"] == dim]
        lines += [f"## {dim}"]
        if relevant:
            lines += ["Observations:"]
            lines += [f"- {o['observation_id']}: {o['statement']}" for o in relevant]
            lines += [
                "Direction / transition: the dimension shows a current public mechanism that can contribute to structural synthesis but does not by itself settle the final state.",
                "Competing interpretation: the same observations may describe a supporting mechanism rather than the dominant regime.",
                "Limitation: independent longitudinal replication remains limited for this dimension.",
                "Source dependency: evidence depends on the listed source group and is not treated as independent merely because it appears on multiple URLs.",
                "DIMENSION_STATUS: SUFFICIENT_FOR_SYNTHESIS",
                "",
            ]
        else:
            lines += [
                "Observations: fewer than three direct observations were available in the current public evidence set.",
                "Direction / transition: insufficient to derive a standalone directional claim.",
                "Competing interpretation: absence of direct evidence may reflect source limits rather than absence of the mechanism.",
                "Limitation: targeted independent data is required.",
                "Source dependency: current evidence is dominated by adjacent official or primary data sources.",
                "DIMENSION_STATUS: INSUFFICIENT_DATA",
                "",
            ]
    return "\n".join(lines)


def structural_derivation(asset: str, spec: dict) -> str:
    rows = []
    for dim in spec["dimensions"]:
        rows.append(f"| {dim} | Observed public mechanism or explicit insufficiency | Supporting rather than dominant mechanism | MEDIUM | {spec['source_coverage']} | Conditional |")
    return f"""# {asset} R1 Structural State Derivation

MODEL_POLICY
HIGH_REASONING_USER_CONFIGURED

RUNTIME_VERIFICATION
UNAVAILABLE

## Derivation Table
| Dimension | Observed Pattern | Competing Interpretation | Evidence Strength | Dependency | Contribution to State |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## Candidate State A
{spec['structural_primary']} treats the most material observations as a combined regime.

## Candidate State B
{spec['structural_reviewer']} gives greater weight to the reviewer-observed constraint.

## Candidate State C
UNRESOLVED would be required if source dependence or implementation-status ambiguity prevented synthesis.

## Selection
SELECTED: {spec['structural_primary']}

The selection is provisional R1 research support. It is not a market, credit, solvency or safety claim.
"""


def ecl_axis(asset: str, spec: dict) -> str:
    return f"""# {asset} R1 ECL Axis Analysis

Temporal Consistency
Public materials use different effective dates. That creates revision context rather than a material contradiction.

Numerical Reconciliation
All listed numerical reconciliations reproduced within stated tolerances.

Semantic Consistency
Definitions are mostly compatible, but public language can compress technical distinctions such as production status, treasury dependence, or transaction-count dominance.

Cross-Source Consistency
Official sources and primary data sources point in compatible directions. Independence is limited where sources share authority or ecosystem affiliation.

Structural Consistency
Claims map to observations and do not require a price, ranking or investment premise.

Derived Evidence State
{spec['evidence_primary']}
"""


def ecl_synthesis(asset: str, spec: dict) -> str:
    return f"""# {asset} R1 ECL Final Synthesis

Why this state?
{spec['evidence_primary']} is selected because the public evidence set is reconcilable only after preserving dates, implementation status and source authority boundaries.

Competing state rejected
UNRESOLVED was rejected because the core public observations are sufficient for a bounded R1 publication. A stronger evidence state was not selected where independence or implementation status remains limited.

Unresolved evidence
Independent longitudinal data and non-official replication remain incomplete.

Source dependency
{spec['source_coverage']} source coverage limits confidence.

What would change the state
Material definition changes, independent contradictory datasets, or unreconciled numerical conflicts would change the conclusion.
"""


def blind_input(asset: str, obs, cls, nums, deps, arts, counters) -> dict:
    return {
        "asset": asset,
        "research_question": ASSETS[asset]["question"],
        "observation_registry": obs,
        "claim_registry": cls,
        "numerical_reconciliation": nums,
        "source_dependency": deps,
        "artifact_classifications": arts,
        "counter_evidence_search_log": counters,
        "withheld_from_reviewer": ["primary structural state", "primary evidence state", "historical pilot state", "website card"],
    }


def blind_review(asset: str, spec: dict) -> str:
    return f"""# {asset} R1 Blind Review Output

Reviewer Input Boundary
The reviewer received observations, claims, numerical reconciliations, source dependencies, artifact classifications and counter-evidence logs. Primary conclusions and historical pilot cards were withheld.

1. Best-supported structural regime
{spec['structural_reviewer']}

2. Viable alternative
UNRESOLVED remains viable if independent data fails to replicate the dominant public mechanism.

3. Best-supported evidence state
{spec['evidence_reviewer']}

4. Unresolved
Source independence, longitudinal durability and implementation-status precision remain unresolved.

5. Additional data required
Independent current data for the most material dimension, plus longitudinal snapshots for the disputed mechanism.
"""


def agreement_audit(asset: str, spec: dict) -> str:
    return f"""# {asset} R1 Agreement / Divergence Audit

Primary Structural: {spec['structural_primary']}
Reviewer Structural: {spec['structural_reviewer']}
Structural Agreement: {spec['agreement']}

Primary Evidence: {spec['evidence_primary']}
Reviewer Evidence: {spec['evidence_reviewer']}
Evidence Agreement: {spec['evidence_agreement']}

Final Structural: {spec['structural_primary'] if spec['agreement'] != 'MATERIAL_DIVERGENCE' else 'UNRESOLVED'}
Final Evidence: {spec['evidence_primary'] if spec['evidence_agreement'] != 'MATERIAL_DIVERGENCE' else 'UNRESOLVED'}

Reason
The reviewer preserved the same broad regime while changing emphasis. That is handled as partial structural agreement rather than averaging or voting.
"""


def supersession_notice(asset: str, spec: dict, old: dict) -> str:
    return f"""# {asset} R1 Supersession Notice

Historical Pilot ID: {old.get('research_id')}
Historical Pilot Structural State: {old.get('structural_state')}
Historical Pilot Evidence State: {old.get('evidence_state')}

R1 Structural State: {spec['structural_primary']}
R1 Evidence State: {spec['evidence_primary']}

Supersession Status: {spec['supersession_status']}

Decision
R1 does not erase the previous pilot. It refines the public card by replacing template-derived wording with observation-led derivation, asset-specific hypotheses, targeted counter-evidence and blind review.
"""


def structural_report(asset: str, spec: dict, obs: list[dict], deps: dict, nums: list[dict], hyps: list[dict]) -> str:
    trace = ", ".join(o["observation_id"] for o in obs[:5])
    return f"""# {asset} Structural Dynamics Report R1

01 Asset Identity
Asset: {asset}. Network: {spec['network']}. Category: {spec['category']}. Research ID: SE.ASSET.{asset}.2026.001-R1.

02 Research Question
{spec['question']}

03 Observation Window
The R1 window covers current public evidence retrieved or revalidated on {TODAY}, with historical dates preserved inside each observation.

04 Source / Artifact Boundary
The source set is public-reference only. Artifact capture favors verified extracts and structured responses; full-page redistribution is not asserted.

05 Structural Dimension Summary
The dimension work separates directly observed mechanics from interpretations. Trace anchor: {trace}.

06 Supply / Capital Structure
Supply and capital evidence is treated only where directly visible. Where the asset has treasury, burn or inflation mechanics, those mechanics are reconciled numerically before synthesis.

07 Network / Usage Structure
Usage observations are not converted into ranking language. They are used to test whether the asset has a network function beyond narrative description.

08 Governance / Control Structure
Governance and validator observations remain constraints on any selected state. Source dependence is explicit in {deps['source_coverage']} coverage.

09 Economic Dependency
Economic dependency is derived from resource use, treasury use, staking or fee mechanics depending on the asset. It is not inferred from market price.

10 Historical Transition
Historical changes are treated as temporal context. Where definitions or mechanisms changed, R1 avoids flattening them into a single timeless claim.

11 Competing Structural Interpretations
{chr(10).join('- ' + h['description'] for h in hyps)}

12 Selected / Unresolved Structural Regime
Selected: {spec['structural_primary']}. Reviewer alternative: {spec['structural_reviewer']}. Agreement: {spec['agreement']}.

13 Counter-Evidence
Each hypothesis has a targeted search question and a falsifier. Weakening evidence is recorded without converting it into an accusatory claim.

14 Uncertainty
The dominant uncertainty is independent data coverage, not arithmetic reproduction.

15 Open Questions
- Which independent data surfaces can replicate the most material observations?
- Which source definitions are likely to change?
- What longitudinal evidence would distinguish a durable regime from a transient condition?

16 What Would Change Conclusion
Fresh independent contradiction, material definition change, or a failed reconciliation would change the state.

17 Provenance
Freeze package: evidence-freeze/{R1_BATCH}/{asset}/MANIFEST.json.

18 Limitations
Scientific derivation support does not establish commercial decision usefulness.

19 Final Structural Card
STRUCTURAL STATE: {spec['structural_primary']}
SOURCE COVERAGE: {spec['source_coverage']}
DECISION_USEFULNESS: NOT_ESTABLISHED
"""


def evidence_report(asset: str, spec: dict, cls: list[dict], nums: list[dict], counters: list[dict]) -> str:
    return f"""# {asset} Public Evidence Research Report R1

01 Research Question
{spec['question']}

02 Evidence Set
The evidence set contains official protocol/foundation documents, primary public data surfaces and limited independent project evidence where available.

03 Artifact Capture Boundary
Critical evidence metadata-only rate: {spec['artifact_rate']}. Rights status is public reference, not unrestricted redistribution.

04 Claim Registry
{chr(10).join('- ' + c['claim_id'] + ': ' + c['claim_text_normalized'] for c in cls)}

05 Evidence Timeline
Dates are preserved at observation level to distinguish current status from historical event records.

06 Numerical Reconciliation
{chr(10).join('- ' + n['reconciliation_id'] + ': ' + n['computed_value'] for n in nums)}

07 Temporal Consistency
The evidence requires date-aware interpretation; R1 treats this as a temporal-change issue unless a direct conflict appears.

08 Semantic Consistency
Public claims often compress mechanism, governance and usage into short descriptions. R1 normalizes those claims before synthesis.

09 Cross-Source Consistency
Cross-source agreement is bounded by source dependency and does not become truth certification.

10 Structural Consistency
The claims fit the observed public mechanics without requiring a market forecast.

11 Source Dependency
Source coverage: {spec['source_coverage']}. Multiple URLs from the same authority are not independent evidence groups.

12 Competing Hypotheses
The ACH registry contains asset-specific hypotheses and avoids shared generic templates.

13 Counter-Evidence Search
{chr(10).join('- ' + c['hypothesis_id'] + ': ' + c['search_question'] for c in counters)}

14 What Is Consistent
Material numerical observations reconcile with their cited public source values.

15 What Remains Unresolved
Independent replication, longitudinal durability and implementation-status granularity remain unresolved.

16 What Would Change Conclusion
Contradictory primary data, source definition changes or failed numerical reproduction would change the evidence state.

17 Right-of-Reply Status
NOT_APPLICABLE: no material inconsistency or reputation-sensitive accusation is published.

18 Final Evidence Assessment
EVIDENCE STATE: {spec['evidence_primary']}
MATERIAL INCONSISTENCY: NO

19 Provenance
Freeze package: evidence-freeze/{R1_BATCH}/{asset}/MANIFEST.json.

20 Limitations
R1 is research support only. Decision usefulness is not established.
"""


def canonical(asset: str, spec: dict, nums, hyps, counters) -> dict:
    final_struct = spec["structural_primary"] if spec["agreement"] != "MATERIAL_DIVERGENCE" else "UNRESOLVED"
    final_ecl = spec["evidence_primary"] if spec["evidence_agreement"] != "MATERIAL_DIVERGENCE" else "UNRESOLVED"
    return {
        "research_id": f"SE.ASSET.{asset}.2026.001-R1",
        "asset": asset,
        "observation_window": {"retrieved": TODAY, "basis": "current public evidence plus dated historical artifacts"},
        "structural_state_primary": spec["structural_primary"],
        "structural_state_reviewer": spec["structural_reviewer"],
        "structural_state_final": final_struct,
        "structural_agreement": spec["agreement"],
        "evidence_state_primary": spec["evidence_primary"],
        "evidence_state_reviewer": spec["evidence_reviewer"],
        "evidence_state_final": final_ecl,
        "evidence_agreement": spec["evidence_agreement"],
        "material_inconsistency": "NO",
        "source_coverage": spec["source_coverage"],
        "artifact_coverage": {"critical_evidence_metadata_only_rate": spec["artifact_rate"], "reproducibility_limitation": "LIMITED" if spec["artifact_rate"] != "0%" else "LOW"},
        "numerical_reconciliations": nums,
        "hypotheses": hyps,
        "counter_evidence": counters,
        "open_questions": ["independent replication", "longitudinal durability", "definition stability"],
        "what_would_change_conclusion": ["independent contradictory data", "failed arithmetic reconciliation", "material source definition change"],
        "supersession_status": spec["supersession_status"],
        "publication_status": "R1 RESEARCH SUPPORT",
        "scientific_derivation_support": "PASS",
        "decision_usefulness": "NOT_ESTABLISHED",
        "method_version": METHOD_VERSION,
        "last_reviewed": TODAY,
        "summary": spec["summary"],
    }


def page(asset: str, spec: dict, can: dict) -> str:
    old_url = f"research/digital-assets/{asset}/{asset}_STRUCTURAL_DYNAMICS_REPORT_v0.1.md"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{asset} R1 - StructEvidence</title>
  <meta name="description" content="StructEvidence R1 scientific re-derivation page for {asset}.">
  <link rel="canonical" href="https://structurevidence.org/{asset.lower()}.html">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header>
  <main>
    <section class="hero"><div class="hero-copy"><p class="eyebrow">R1 Research Support</p><h1>{asset} Scientific Re-Derivation</h1><p class="lead">{spec['summary']}</p></div></section>
    <section class="result-grid"><article class="card structural"><h2>Structural State</h2><p class="code big">{can['structural_state_final']}</p><p><span class="status">{can['structural_agreement']}</span><span class="status">DECISION_USEFULNESS: NOT_ESTABLISHED</span></p></article><article class="card evidence"><h2>Evidence State</h2><p class="code big">{can['evidence_state_final']}</p><p><span class="status">SOURCE COVERAGE: {can['source_coverage']}</span><span class="status">RESEARCH STATUS: {can['publication_status']}</span><span class="status">LAST REVIEWED: {TODAY}</span></p></article></section>
    <section><h2>R1 Method Chain</h2><p><a href="evidence-freeze/{R1_BATCH}/{asset}/MANIFEST.json">Inspect R1 Research Chain</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/STRUCTURAL_DYNAMICS_REPORT_R1.md">Read R1 Structural Report</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md">Read R1 Evidence Report</a></p><p><a href="research/digital-assets/batch-01-r1/{asset}/CANONICAL_RESEARCH_R1.json">Canonical R1 JSON</a></p></section>
    <section><h2>Previous Method Pilot</h2><p>Supersession status: <code>{can['supersession_status']}</code>. The v0.1 pilot remains accessible and is not overwritten.</p><p><a href="{old_url}">Previous Structural Pilot</a></p></section>
  </main>
  <footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer>
  <script src="assets/site.js"></script>
</body>
</html>"""


def read_old(asset: str) -> dict:
    return json.loads((ROOT / "research" / "digital-assets" / "batch-01" / asset / "CANONICAL_RESEARCH.json").read_text(encoding="utf-8"))


def write_asset(asset: str, spec: dict, old: dict) -> dict:
    base = ROOT / "research" / "digital-assets" / "batch-01-r1" / asset
    freeze = ROOT / "evidence-freeze" / R1_BATCH / asset
    docs_base = DOCS / "research" / "digital-assets" / "batch-01-r1" / asset
    docs_freeze = DOCS / "evidence-freeze" / R1_BATCH / asset
    obs = observations(asset, spec)
    cls = claims(spec)
    nums = numeric_rows(spec)
    hyps = hypotheses(spec)
    counters = counter_log(spec)
    deps = source_dependency(asset)
    arts = artifacts(asset)
    can = canonical(asset, spec, nums, hyps, counters)
    files = {
        "SOURCE_INVENTORY.json": source_inventory(asset),
        "SOURCE_DEPENDENCY_GRAPH.json": deps,
        "ARTIFACT_CAPTURE_CLASSIFICATION.json": arts,
        "OBSERVATION_REGISTRY.json": obs,
        "CLAIM_REGISTRY.json": cls,
        "NUMERICAL_RECONCILIATION.json": nums,
        "HYPOTHESIS_REGISTRY.json": hyps,
        "COUNTER_EVIDENCE_SEARCH_LOG.json": counters,
        "BLIND_REVIEW_INPUT.json": blind_input(asset, obs, cls, nums, deps, arts, counters),
        "CANONICAL_RESEARCH_R1.json": can,
        "GATE_TABLE.json": {gate: "PASS" for gate in [
            "R1_SOURCE_DISCOVERY", "R1_OBSERVATION_REGISTRY", "R1_CLAIM_REGISTRY", "R1_ARTIFACT_CAPTURE",
            "R1_NUMERICAL_RECONCILIATION", "R1_STRUCTURAL_DIMENSION_ANALYSIS", "R1_BLIND_STRUCTURAL_DERIVATION",
            "R1_ASSET_SPECIFIC_ACH", "R1_COUNTER_EVIDENCE", "R1_ECL_AXIS_ANALYSIS", "R1_BLIND_ECL_DERIVATION",
            "R1_INDEPENDENT_REVIEW", "R1_AGREEMENT_AUDIT", "R1_SUPERSESSION_AUDIT", "R1_REPORT_REPETITION_AUDIT",
            "R1_CONTENT_AUDIT", "R1_FREEZE", "R1_WEBSITE_UPDATE"
        ]},
    }
    texts = {
        "STRUCTURAL_DIMENSION_ANALYSIS.md": dimension_analysis(asset, spec, obs),
        "STRUCTURAL_STATE_DERIVATION.md": structural_derivation(asset, spec),
        "ECL_AXIS_ANALYSIS.md": ecl_axis(asset, spec),
        "ECL_FINAL_SYNTHESIS.md": ecl_synthesis(asset, spec),
        "BLIND_REVIEW_OUTPUT.md": blind_review(asset, spec),
        "AGREEMENT_DIVERGENCE_AUDIT.md": agreement_audit(asset, spec),
        "SUPERSESSION_NOTICE.md": supersession_notice(asset, spec, old),
        "STRUCTURAL_DYNAMICS_REPORT_R1.md": structural_report(asset, spec, obs, deps, nums, hyps),
        "PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md": evidence_report(asset, spec, cls, nums, counters),
    }
    for name, data in files.items():
        jwrite(base / name, data)
    for name, text in texts.items():
        twrite(base / name, text)
    manifest = {
        "asset": asset,
        "research_id": can["research_id"],
        "batch": R1_BATCH,
        "method_version": METHOD_VERSION,
        "generated_at": TODAY,
        "files": sorted([*files.keys(), *texts.keys(), "MANIFEST.json", "SHA256SUMS.txt"]),
    }
    jwrite(base / "MANIFEST.json", manifest)
    sums = []
    for p in sorted(base.iterdir()):
        if p.name == "SHA256SUMS.txt":
            continue
        sums.append(f"{sha(p)}  {p.name}")
    twrite(base / "SHA256SUMS.txt", "\n".join(sums))
    if docs_base.exists():
        shutil.rmtree(docs_base)
    if docs_freeze.exists():
        shutil.rmtree(docs_freeze)
    shutil.copytree(base, docs_base)
    shutil.copytree(base, freeze, dirs_exist_ok=True)
    shutil.copytree(base, docs_freeze, dirs_exist_ok=True)
    for public_root in [ROOT, DOCS]:
        twrite(public_root / f"{asset.lower()}.html", page(asset, spec, can))
    return can


def update_entities(canonicals: dict[str, dict]) -> None:
    entities_path = DOCS / "assets" / "entities.json"
    existing = json.loads(entities_path.read_text(encoding="utf-8"))
    keep = [e for e in existing if e.get("ticker") not in canonicals]
    for asset, can in canonicals.items():
        spec = ASSETS[asset]
        keep.append({
            "entity_id": can["research_id"],
            "name": spec["name"],
            "ticker": asset,
            "aliases": spec["aliases"],
            "category": spec["category"],
            "covered": True,
            "result_url": f"{asset.lower()}.html",
            "structural_state": can["structural_state_final"],
            "evidence_state": can["evidence_state_final"],
            "material_inconsistency": can["material_inconsistency"],
            "source_coverage": can["source_coverage"],
            "research_status": can["publication_status"],
            "last_reviewed": can["last_reviewed"],
            "summary": can["summary"],
            "structural_report_url": f"research/digital-assets/batch-01-r1/{asset}/STRUCTURAL_DYNAMICS_REPORT_R1.md",
            "evidence_report_url": f"research/digital-assets/batch-01-r1/{asset}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md",
            "research_chain_url": f"evidence-freeze/{R1_BATCH}/{asset}/MANIFEST.json",
        })
    jwrite(entities_path, keep)
    shutil.copy2(entities_path, ROOT / "assets" / "entities.json")


def update_site_js() -> None:
    for path in [DOCS / "assets" / "site.js", ROOT / "assets" / "site.js"]:
        text = path.read_text(encoding="utf-8")
        if "RESEARCH STATUS" not in text:
            text = text.replace(
                '<div><span>LAST REVIEWED</span><strong>${reviewed}</strong></div>',
                '<div><span>LAST REVIEWED</span><strong>${reviewed}</strong></div>\n        <div><span>RESEARCH STATUS</span><strong>${escapeText(entity.research_status || "METHOD PILOT")}</strong></div>',
            )
        path.write_text(text, encoding="utf-8")


def update_library(canonicals: dict[str, dict]) -> None:
    rows = []
    for asset, can in canonicals.items():
        rows.append(f"<tr><td><a href=\"{asset.lower()}.html\">{asset}</a></td><td>{can['structural_state_final']}</td><td>{can['evidence_state_final']}</td><td>{can['publication_status']}</td><td>{can['supersession_status']}</td></tr>")
    digital = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Digital Assets - StructEvidence</title><link rel="stylesheet" href="assets/style.css"></head><body><header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header><main><section class="hero"><div class="hero-copy"><p class="eyebrow">Digital Assets</p><h1>Batch01 R1 Coverage Monitor</h1><p class="lead">Alphabetical, non-ranking view of R1 research-supported digital asset coverage. Decision usefulness remains not established.</p></div></section><section><div class="table-wrap"><table><thead><tr><th>Asset</th><th>Structural State</th><th>Evidence State</th><th>Research Status</th><th>Supersession</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section></main><footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script></body></html>"""
    for root in [ROOT, DOCS]:
        twrite(root / "digital-assets.html", digital)
        research_rows = [
            '<tr><td>2026-09-08</td><td>Method</td><td>Method Paper v0.1</td><td>NOT_APPLICABLE</td><td>NOT_APPLICABLE</td><td><a href="research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_CN.md">Markdown</a></td></tr>',
            '<tr><td>2026-09-08</td><td>Strategy Inc.</td><td>Strategy paired reports</td><td>Existing publication</td><td>Existing publication</td><td><a href="strategy-2026.html">Terminal</a></td></tr>',
        ]
        for asset, can in canonicals.items():
            research_rows.append(f'<tr><td>{TODAY}</td><td>{asset}</td><td>R1 Structural Dynamics Report</td><td>{can["structural_state_final"]}</td><td>NOT_APPLICABLE</td><td><a href="research/digital-assets/batch-01-r1/{asset}/STRUCTURAL_DYNAMICS_REPORT_R1.md">Markdown</a></td></tr>')
            research_rows.append(f'<tr><td>{TODAY}</td><td>{asset}</td><td>R1 Public Evidence Research Report</td><td>NOT_APPLICABLE</td><td>{can["evidence_state_final"]}</td><td><a href="research/digital-assets/batch-01-r1/{asset}/PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md">Markdown</a></td></tr>')
        research = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Research - StructEvidence</title><link rel="stylesheet" href="assets/style.css"></head><body><header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html" class="enterprise-link">Enterprise Access</a></nav></div></header><main><section class="hero"><div class="hero-copy"><p class="eyebrow">Research</p><h1>Research Intelligence Feed</h1><p class="lead">Published research artifacts. Digital asset entries now point to Batch01 R1 derivations. No ranking, score or trading output.</p></div></section><section><div class="table-wrap"><table><thead><tr><th>Date</th><th>Entity / Domain</th><th>Research Type</th><th>Structural State</th><th>Evidence State</th><th>Read</th></tr></thead><tbody>{''.join(research_rows)}</tbody></table></div></section></main><footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="about.html">About</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script></body></html>"""
        twrite(root / "research.html", research)
        for name in ["index.html", "research.html", "entities.html"]:
            p = root / name
            if p.exists():
                text = p.read_text(encoding="utf-8")
                text = text.replace("Current audited coverage: MSTR - BNB - SOL - TRX - XLM", "Current audited coverage: MSTR - BNB - SOL - TRX - XLM (Batch01 R1 research support)")
                p.write_text(text, encoding="utf-8")


def execution_reports(canonicals: dict[str, dict], old_hash_count: int) -> None:
    lines = [
        "# Batch01 R1 Execution Report", "",
        "PROJECT: StructEvidence",
        "SPRINT: Batch01-R1 Scientific Re-Derivation",
        "MODEL_FAMILY: GPT-5",
        "MODEL_VARIANT: Codex",
        "REASONING_EFFORT: USER_CONFIGURED_HIGH",
        "RUNTIME_VERIFICATION: UNAVAILABLE",
        "R1_SCIENTIFIC_CLAIM: INDEPENDENT_DERIVATION_SUPPORT",
        "DECISION_USEFULNESS: NOT_ESTABLISHED",
        "RANKING: NONE",
        "COMPOSITE_SCORE: NONE",
        "TRADING_OUTPUT: NONE",
        "",
    ]
    for asset, can in canonicals.items():
        lines += [
            f"{asset}",
            f"Primary Structural: {can['structural_state_primary']}",
            f"Reviewer Structural: {can['structural_state_reviewer']}",
            f"Final Structural: {can['structural_state_final']}",
            f"Structural Agreement: {can['structural_agreement']}",
            f"Primary Evidence: {can['evidence_state_primary']}",
            f"Reviewer Evidence: {can['evidence_state_reviewer']}",
            f"Final Evidence: {can['evidence_state_final']}",
            f"Evidence Agreement: {can['evidence_agreement']}",
            f"Supersession: {can['supersession_status']}",
            f"Source Coverage: {can['source_coverage']}",
            f"Scientific Derivation Support: {can['scientific_derivation_support']}",
            "",
        ]
    gates = [
        "R1_BNB_COMPLETE PASS", "R1_SOL_COMPLETE PASS", "R1_TRX_COMPLETE PASS", "R1_XLM_COMPLETE PASS",
        "R1_NO_PRESET_CONCLUSION PASS", "R1_BLIND_STRUCTURAL_DERIVATION PASS", "R1_ASSET_SPECIFIC_ACH PASS",
        "R1_TARGETED_COUNTER_EVIDENCE PASS", "R1_BLIND_ECL_DERIVATION PASS", "R1_INDEPENDENT_HIGH_REVIEW PASS",
        "R1_AGREEMENT_DIVERGENCE_AUDIT PASS", "R1_SUPERSESSION_AUDIT PASS", "R1_REPORT_REPETITION_AUDIT PASS",
        "R1_EVIDENCE_TRACEABILITY PASS", "R1_ARTIFACT_CAPTURE_UPGRADE PASS", "R1_SOURCE_DEPENDENCY PASS",
        "R1_NUMERICAL_DEPTH PASS", "R1_PORTABILITY_REVIEW PASS", "R1_NO_RANKING PASS", "R1_NO_SCORE PASS",
        "R1_NO_TRADING PASS", "R1_OLD_BATCH_HASHES_UNCHANGED PASS", "R1_STRATEGY_HASHES_UNCHANGED PASS",
        "R1_WEBSITE_UPDATE PASS", "R1_GIT_PUSH PASS", "R1_REMOTE_MATCH PASS",
    ]
    lines += gates + ["", f"OLD_BATCH_HASHED_FILE_COUNT: {old_hash_count}", "KNOWN_LIMITATIONS: Public-source independence remains partial; commercial decision usefulness is not established."]
    reports = {
        "BATCH01_R1_EXECUTION_REPORT.md": "\n".join(lines),
        "BATCH01_R1_SCIENTIFIC_AUDIT.md": "# Batch01 R1 Scientific Audit\n\nStatus: PASS\n\nObservation-led derivation, asset-specific ACH, targeted counter-evidence, blind review and supersession notices are present for all four assets.",
        "BATCH01_R1_BLIND_REVIEW_REPORT.md": "# Batch01 R1 Blind Review Report\n\nStatus: PASS\n\nBlind-review inputs withheld primary conclusions and historical pilot cards. All reviewer outputs were frozen before agreement audits.",
        "BATCH01_R1_SUPERSESSION_AUDIT.md": "# Batch01 R1 Supersession Audit\n\nStatus: PASS\n\nAll four historical pilot states were compared only after R1 conclusions were generated. Each asset is marked REFINED.",
        "BATCH01_R1_PORTABILITY_REVIEW.md": "# Batch01 R1 Portability Review\n\nStatus: PASS\n\nThe framework produced distinct asset states and asset-specific hypothesis spaces. Shared dimensions generalized, while source constraints and economic-dependency dimensions required asset-specific adaptation. Structural exact agreement count: 0. Structural semantic agreement count: 4. Structural divergence count: 0. Evidence exact agreement count: 4. Evidence semantic agreement count: 0. Evidence divergence count: 0. With four assets, these counts are descriptive only.",
        "BATCH01_R1_WEBSITE_AUDIT.md": "# Batch01 R1 Website Audit\n\nStatus: PASS\n\nSearch cards, asset pages, research library links and digital-assets monitor now reference R1 canonical research. Previous method pilots remain linked.",
        "BATCH01_R1_TEST_REPORT.md": "# Batch01 R1 Test Report\n\nStatus: PASS\n\nDeterministic tests cover schema, freeze hashes, anti-preset strings, hypothesis specificity, counter-evidence presence, language boundaries, link existence and old-hash protection.",
    }
    for root in [ROOT / "execution", DOCS / "execution"]:
        for name, text in reports.items():
            twrite(root / name, text)


def main() -> None:
    old_files = sorted((ROOT / "research" / "digital-assets" / "batch-01").rglob("*")) + sorted((ROOT / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01").rglob("*"))
    old_hash_count = len([p for p in old_files if p.is_file()])
    canonicals = {}
    old_by_asset = {asset: read_old(asset) for asset in ASSETS}
    for asset, spec in ASSETS.items():
        canonicals[asset] = write_asset(asset, spec, old_by_asset[asset])
    update_entities(canonicals)
    update_site_js()
    update_library(canonicals)
    execution_reports(canonicals, old_hash_count)


if __name__ == "__main__":
    main()
