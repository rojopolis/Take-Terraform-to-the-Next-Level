module "google-cloud-ip-range" {
    source = "../"
}

output "gcp-ipv4-ranges" {
    value = module.google-cloud-ip-range.ip_v4_cidrs
}

output "gcp-ipv6-ranges" {
    value = module.google-cloud-ip-range.ip_v6_cidrs
}

output "gcp-ranges" {
    value = module.google-cloud-ip-range.cidrs
}