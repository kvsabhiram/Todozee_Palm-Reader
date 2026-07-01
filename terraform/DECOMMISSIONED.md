# Palm-Reader Terraform — DECOMMISSIONED (2026-07-01)

This standalone stack used to provision a **dedicated `g5.xlarge` (A10G)** box
for the Palm-Reader service. That service has been **consolidated onto the
Past-Life GPU box** to share one GPU and cut a g5.xlarge.

## What changed (done manually / imperatively via SSM)
- App `/opt/todozee-palm-reader` (repo + venv + Gemma-4-E2B model cache) was
  copied to the **Past-Life** box `i-07d3af0a96c205a0b` (EIP `52.66.61.154`).
- It runs there as systemd `todozee-palm-reader.service` on **:7003**, fronted
  by that box's **Caddy** vhost `palmreader.chatbucket.chat` (25 MB body limit).
- DNS `palmreader.chatbucket.chat` was repointed `13.200.0.60` → `52.66.61.154`.
- **HTTPS + real inference verified** on the new host.
- This stack's own instance **`i-0221ff9019e7d8a1e`** was **STOPPED** (not
  terminated) and tagged `todozee-palm-reader-RETIRED-rollback` as a temporary
  rollback safety net.

## Current state of this Terraform
The `.tf` files are **left intact on purpose**. As of now they still match
reality (the box exists, just stopped), so:
- Do **NOT** run `terraform apply` casually — Terraform doesn't manage
  stop/start, so a plan should be a no-op, but keep the state safe.
- Ownership of the Palm-Reader *app* now belongs to the **Past-Life repo's**
  Terraform / deploy pipeline, not this one.

## Rollback (if the consolidated box misbehaves)
1. Start the old box: `aws ec2 start-instances --instance-ids i-0221ff9019e7d8a1e`
2. It gets a **new** public IP (the old EIP `13.200.0.60` was released when...
   actually it was a dynamic public IP, not an EIP — confirm the new IP).
3. Repoint `palmreader.chatbucket.chat` back to that IP in Cloudflare.

## Full teardown (when Past-Life is proven stable)
Run in this directory to remove ALL of this stack's resources (instance, EIP,
security group, IAM role/profile, key pair, CloudWatch alarms/log groups):

```bash
terraform destroy
```

Then this `terraform/` directory can be deleted from the repo (or the whole
repo archived), since the service lives on the Past-Life box.

> NOTE: State is **local** (no remote backend). Make sure you run `destroy`
> from the same machine/location that holds this stack's `terraform.tfstate`,
> otherwise Terraform won't know about the existing resources.
