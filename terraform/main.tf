provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.access_secret}"
  region = "${var.aws_region}"
}

resource "aws_instance" "SMACK" {
  ami = "${lookup(var.aws_amis, var.aws_region)}"
  instance_type = "t2.medium"
  security_groups = ["${aws_security_group.all-allow.name}"]
  key_name = "${var.key_name}"

  tags {
    Name="SMACK"
  }

  connection {
    user = "ec2-user"
    private_key = "${file(var.key_path)}"
  }

  provisioner "file" {
    source = "setup.sh"
    destination = "~/setup.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y docker",
      "sudo service docker start",
      "sudo usermod -a -G docker ec2-user",
      "exit",
      ]
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x ~/setup.sh",
      "~/setup.sh ${aws_instance.SMACK.public_ip}"
    ]
  }
}

resource "aws_instance" "WebServer" {
  ami = "ami-d8bdebb8"
  instance_type = "t2.medium"
  security_groups = ["${aws_security_group.all-allow.name}"]
  key_name = "${var.key_name}"

  tags {
    Name="Bigdata_WebServer"
  }

  connection {
    user = "ubuntu"
    private_key = "${file(var.key_path)}"
  }

  provisioner "file" {
    source = "../data-producer.py"
    destination = "~/data-producer.py"
  }

  provisioner "file" {
    source = "../data-storage.py"
    destination = "~/data-storage.py"
  }

  provisioner "file" {
    source = "py_packages.sh"
    destination = "~/py_packages.sh"
  }

  provisioner "file" {
    source = "start-server.sh"
    destination = "~/start-server.sh"
  }

  provisioner "file" {
    source = "log.io.config/harvester.conf"
    destination = "~/harvester.conf"
  }

  provisioner "file" {
    source = "nodejs.zip"
    destination = "~/nodejs.zip"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x ~/py_packages.sh",
      "chmod +x ~/start_server.sh",
      "~/py_packages.sh",
      "~/start_server.sh ${aws_instance.SMACK.public_ip}",
    ]
  }
}

resource "aws_security_group" "all-allow" {
  name = "all-allow"

  ingress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}