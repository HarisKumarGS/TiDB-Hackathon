variable "microservices" {
  description = "Map of microservices with image, cpu, memory, env, and desired_count"
  type = map(object({
    image          = string
    cpu            = number
    memory         = number
    desired_count  = number
    container_port = number
    environment    = map(string)
    health_path    = optional(string, "/health")
  }))
  default = {
    auth = {
      image          = "public.ecr.aws/amazonlinux/amazonlinux:latest"
      cpu            = 256
      memory         = 512
      desired_count  = 1
      container_port = 8080
      environment    = {}
      health_path    = "/health"
    }
  }
}

resource "aws_cloudwatch_log_group" "service" {
  for_each = var.microservices
  name     = "/ecs/${var.project_name}/${var.environment}/${each.key}"
  retention_in_days = 14
  tags = local.common_tags
}

resource "aws_ecs_task_definition" "service" {
  for_each                 = var.microservices
  family                   = "${var.project_name}-${var.environment}-${each.key}"
  cpu                      = each.value.cpu
  memory                   = each.value.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = each.key
      image     = each.value.image
      essential = true
      portMappings = [
        {
          containerPort = each.value.container_port
          hostPort       = each.value.container_port
          protocol       = "tcp"
        }
      ]
      environment = [for k, v in each.value.environment : { name = k, value = v }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.service[each.key].name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${each.value.container_port}${lookup(each.value, "health_path", "/health")} || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }
  ])
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
  tags = local.common_tags
}

resource "aws_ecs_service" "service" {
  for_each            = var.microservices
  name                = "${var.project_name}-${var.environment}-${each.key}"
  cluster             = aws_ecs_cluster.this.id
  task_definition     = aws_ecs_task_definition.service[each.key].arn
  desired_count       = each.value.desired_count
  launch_type         = "FARGATE"
  enable_execute_command = true

  network_configuration {
    assign_public_ip = false
    subnets          = [for s in aws_subnet.private : s.id]
    security_groups  = [aws_security_group.services_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.default.arn
    container_name   = each.key
    container_port   = each.value.container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = local.common_tags
}


