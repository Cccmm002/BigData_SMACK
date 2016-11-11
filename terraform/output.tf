output "SMACK_ip" {
  value="${aws_instance.SMACK.public_ip}"
}

output "Server_ip" {
  value="${aws_instance.WebServer.public_ip}"
}