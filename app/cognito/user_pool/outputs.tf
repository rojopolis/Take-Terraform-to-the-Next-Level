output "my90_user_pool_arn" {
    description = "Cognito User Pool resource"
    value       = "${aws_cognito_user_pool.my90_user_pool.arn}"
}

output "my90_user_pool_client_id" {
    description = "Cognito User Pool Client ID"
    value       = "${aws_cognito_user_pool_client.my90_user_pool_client.id}"
}

output "my90_user_pool_resource_server_identifier" {
    description = "Cognito User Pool Client ID"
    value       = "${aws_cognito_resource_server.my90_user_pool_resource_server.identifier}"
}