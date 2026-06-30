# ─────────────────────────────────────────────────────────────────────
# CloudWatch log groups for the logs the CW agent ships (see the
# logs.collect_list in user_data.sh.tpl). Declared here so the retention
# policy is codified in Terraform rather than relying on the agent's
# auto-created groups (which default to never-expire).
#
# NOTE: if the agent creates these before the first apply, import them:
#   terraform import aws_cloudwatch_log_group.bootstrap /todozee-palm-reader/bootstrap
#   terraform import aws_cloudwatch_log_group.app       /todozee-palm-reader/app
# ─────────────────────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "bootstrap" {
  name              = "/${var.project_name}/bootstrap"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/${var.project_name}/app"
  retention_in_days = var.log_retention_days
}
