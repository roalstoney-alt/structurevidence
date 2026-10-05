# Evidence visibility consent — OIL-CAND-001

Choose exactly one visibility boundary for each evidence item:

- [ ] `PUBLIC` — permits limited public projection of the claim, future status, as-of boundary, evidence type/identifier, and scope summary. The raw document need not be public.
- [ ] `AUTHORIZED_BUYER` — may later be shown only to a qualified buyer under a proven authorization mechanism. Until that mechanism exists, the item remains private.
- [ ] `TRANSACTION_PRIVATE` — restricted to an identified transaction or explicitly authorized party and excluded from public exports.

Evidence item/document identifier: ____________________  
Applicable Claim ID(s): ____________________  
Selected visibility: ____________________  
Additional restrictions: ____________________  
Authorized signatory/name: ____________________  
Date: ____________________

If authorization, scope, or consent is missing or cannot be proven, StructEvidence fails closed and keeps the evidence private. A Demand or supplier response does not itself grant access.

