output "my90_rest_api_id" {
    description = "API Gateway resource"
    value       = "${aws_api_gateway_rest_api.my90_api.id}"
}

output "my90_rest_api_execution_arn" {
    description = "API Gateway execution arn"
    value       = "${aws_api_gateway_rest_api.my90_api.execution_arn}"
}