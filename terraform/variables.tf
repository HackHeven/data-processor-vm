variable "aws_region" {
  description = "AWS Region to deploy to"
  default     = "us-east-1"
}

variable "key_name" {
  description = "Name of an existing AWS Key Pair in your account to allow SSH access to the VM"
  type        = string
  default     = "my-key-pair"
}
