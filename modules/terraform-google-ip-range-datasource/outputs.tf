output "ip_v4_cidrs" {
    description = "List of CIDR blocks of IPv4 addresses."
    value       = local.ip_v4_cidrs
}

output "ip_v6_cidrs" {
    description = "List of CIDR blocks of IPv6 addresses."
    value       = local.ip_v6_cidrs
}

output "cidrs" {
    description = "List of CIDR blocks (IPv4 & IPv6)"
    value       = local.cidrs
}