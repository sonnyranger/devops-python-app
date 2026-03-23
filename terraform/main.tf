provider "aws" {
  region = "eu-central-1"
}

resource "aws_instance" "k8s_node" {
  ami           = "ami-123456"
  instance_type = "t2.micro"

  tags = {
    Name = "k8s-node"
  }
}