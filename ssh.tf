resource "tls_private_key" "vm_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

locals {
  ssh_public_key = tls_private_key.vm_ssh.public_key_openssh
}

