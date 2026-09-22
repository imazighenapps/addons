# Portal flow

1. A portal customer opens **My Account > PestOps**.
2. The portal exposes only sites, visits, treatment certificates and service requests belonging to the customer's commercial partner.
3. A new request can be linked to a site and optionally to a visit.
4. A request with type **Re-Service** and a related visit automatically creates an `pest.reservice` in state `open`.
5. Internal users process the request from **PestOps > Service Requests**.
6. The customer can revisit the request page to see its status and internal response published through `response_notes`.

Security design: portal reads and writes use `sudo()` only after explicit commercial-partner ownership checks in the controller. This keeps portal users independent from backend PestOps ACLs.
