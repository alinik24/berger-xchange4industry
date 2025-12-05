# IDS & Data Sovereignty Strategy

## The Problem
In the manufacturing supply chain, sharing sensitive data (like CAD files, BOMs, or Pricing) is risky. Once a file is emailed, the owner loses control over it.

## The Solution: Gaia-X / IDS
We use the **International Data Spaces (IDS)** standard to attach **Usage Policies** to data *before* it leaves the provider's domain.

### Implemented Policies (Mocked)

In this prototype, we demonstrate the following Usage Control patterns:

1. **N-Times Usage**:
   - *Logic*: The consumer can only download the asset (e.g., BOM) a specific number of times (e.g., 5).
   - *Implementation*: The EDC connector tracks the access count in its contract agreement store.

2. **Time-Restricted Access**:
   - *Logic*: The asset is only available until a specific date (e.g., "Contract Expiry").
   - *Implementation*: The policy evaluates `CurrentTime < ExpiryTime`.

3. **Purpose-Restricted**:
   - *Logic*: Data can only be used for a specific purpose (e.g., "Quality Control").
   - *Implementation*: Requires the consumer to present a verifiable credential or claim stating their intent.

## Technical Implementation (Eclipse EDC)

The **Eclipse Dataspace Components (EDC)** handle the negotiation:

1. **Asset Creation**: Berger registers the "Digital Twin" API as an Asset in the Provider EDC.
2. **Policy Definition**: Berger defines a Policy (e.g., `use-permission` if `date < 2024-01-01`).
3. **Contract Definition**: Links the Asset to the Policy.
4. **Negotiation**: When Stripmeier (Consumer) requests the data, the Consumer EDC and Provider EDC perform a handshake to agree on the terms.
5. **Data Transfer**: If agreed, the Provider EDC proxies the data from the Backend to the Consumer.
