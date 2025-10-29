# Variables
variable "lambda_name" {}
variable "role_name" {}
variable "log_retention_in_days" { default = 14 }
variable "image_uri" {}
variable "timeout" { default = 10 }
variable "memory_size" { default = 128 }
variable "input_bucket_arn" {}
variable "output_bucket_arn" {}


variable "environment_variables" { 
    type = map(string) 
    default = {} 
}

variable "default_tags" {
  type = map(string)
  description = "Default tags to apply to all resources"
}