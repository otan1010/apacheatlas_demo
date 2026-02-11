variable "location" {
  type    = string
  default = "westeurope"
}

variable "prefix" {
  type    = string
  default = "atlasdev"
}

variable "admin_username" {
  type    = string
  default = "azureuser"
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}

# Lock down inbound rules to your IP (e.g. "203.0.113.10/32")
variable "my_ip_cidr" {
  type = string
}

# If true, opens 21000 to your IP. If false, keep closed and use SSH tunnel.
variable "open_atlas_port" {
  type    = bool
  default = false
}

# VM sizing: Atlas is heavy; 4 vCPU / 16 GB is a good dev baseline.
variable "vm_size" {
  type    = string
  default = "Standard_D4s_v5"
}

variable "os_disk_gb" {
  type    = number
  default = 64
}
