# You will need to modify the key value in the backend block to a unique value for your assignment.

provider "aws" {
  region = var.region_name
  profile = var.aws_profile

}
data "aws_caller_identity" "current" {}


terraform {
  backend "local" {
    path = "./terraform.tfstate"
    #there were issues with the IAM where i couldnt tag the bucket after making, so just using local now
  }
  # backend "s3" {
  #   bucket         = "bucket"
  #   ## update the key value to a unique value for your assignment
  #   key            = "key"
  #   region         = "us-west-2"
  #   # dynamodb_table = "nmd-training-tf-state-lock-table" #apparently deprecated?
  #   use_lockfile = true   
  #   encrypt        = true                   # Encrypts the state file at rest
  # }
}
