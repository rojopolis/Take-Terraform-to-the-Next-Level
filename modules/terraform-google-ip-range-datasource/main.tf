data "external" "google_cloud_cidrs" {
    program = [
        "python3",
        "${path.module}/scripts/datasource.py",
    ]
}

locals {
    ip_v4_cidrs = distinct(compact(split(" ", data.external.google_cloud_cidrs.result["ipv4Cidrs"])))
    ip_v6_cidrs = distinct(compact(split(" ", data.external.google_cloud_cidrs.result["ipv6Cidrs"])))
    cidrs = concat(local.ip_v4_cidrs, local.ip_v6_cidrs)
}