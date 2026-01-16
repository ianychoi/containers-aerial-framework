---
title: "Delete Resource"
weight: 81
---

# 🧹 Resource Cleanup

After completing the workshop, clean up created resources to prevent cost incurrence.

## Delete Resources via AWS Console

### 1. Delete Amazon EKS Cluster

Delete the cluster from the Amazon EKS console:

![Delete Cluster](/static/delete-cluster.png)

## Resource Cleanup via Command Line

### **Local Environment Cleanup**

```bash
# Clean up Docker containers and images
docker system prune -a

# Remove unnecessary images
docker rmi $(docker images -q)
```

### **AWS Resource Cleanup**

```bash
# Delete ECR images
aws ecr batch-delete-image \
  --repository-name sionna-research \
  --image-ids imageTag=latest

# Delete EKS cluster (if expanded environment was built)
eksctl delete cluster --name eks-automode
```

## Important Notes

- Ensure important data and configurations are backed up before deleting resources
- When deleting an EKS cluster, all connected resources (node groups, load balancers, etc.) will also be deleted
- ECR image deletion is irreversible, so proceed with caution

