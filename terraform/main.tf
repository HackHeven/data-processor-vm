# This Terraform script provisions a standard AWS EC2 Ubuntu instance
# and configures it to automatically install Docker on startup.
# We chose AWS for the example, but the concepts apply identically to GCP or Azure.

provider "aws" {
  region = var.aws_region
}

# Create a security group to allow SSH and port 8000 (API)
resource "aws_security_group" "app_sg" {
  name        = "data-processor-sg"
  description = "Allow SSH and API traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: In prod, restrict this to your IP or load balancer
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Find the latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Launch the EC2 instance
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro" # Free tier eligible limit
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  # User data script: Runs as root on the first boot of the VM.
  # This perfectly bridges Terraform with the Docker requirement.
  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y ca-certificates curl gnupg lsb-release
              mkdir -p /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
              apt-get update
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "DataProcessorServer"
  }
}

output "public_ip" {
  value       = aws_instance.app_server.public_ip
  description = "The public IP of the newly created VM"
}
