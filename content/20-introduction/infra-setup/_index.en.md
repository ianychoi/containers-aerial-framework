---
title: "Infrastructure Setup"
weight: 18
---

Amazon EKS provides large-scale scalability and useful management features for containers.
Here, we explain Amazon EKS and Auto Mode for those who want to understand the infrastructure in detail.

::alert[All infrastructure components have been pre-deployed and configured. You can focus entirely on learning and experimenting with research applications without worrying about setup complexities.]{type="success"}

## Pre-Configured Infrastructure Overview

Your workshop environment includes a fully operational Amazon EKS cluster with the following components:

### 🚀 Amazon EKS Cluster with Auto Mode

The workshop uses **Amazon EKS Auto Mode**, a managed AWS Kubernetes Service that eliminates the operational overhead of managing compute, storage, and networking resources.

#### What is EKS Auto Mode?

EKS Auto Mode provides a fully managed Kubernetes experience where AWS handles:

- **Automatic compute provisioning** - No need to manually create or manage EC2 instances
- **Dynamic scaling** - Automatically adjusts capacity based on workload demands
- **Patch management** - Automated OS and Kubernetes component updates
- **Cost optimization** - Intelligent instance selection and Spot instance integration

:::code{language=bash showCopyAction=true}
# View EKS cluster details
kubectl cluster-info

# Check EKS Auto Mode configuration
kubectl get nodes -L eks.amazonaws.com/compute-type
:::

### 💻 Node Pool Configuration

The cluster includes dedicated node pools optimized for different workload types:

#### 1. **General Purpose Nodes (Multi-Architecture)**
- **Instance Types**: Latest generation compute (C), memory (M), and general purpose (R) optimized instances
  - **AWS Graviton (ARM64)**: ARM-based instances providing up to 40% better price-performance
  - **x86 (AMD/Intel)**: Traditional x86 architecture instances
- **Architecture Support**: Multi-arch (amd64/arm64) with automatic selection based on workload compatibility
- **Purpose**: Running general workloads, web services, and control plane components
- **Cost Optimization**: 
  - Graviton instances provide up to 40% better price-performance vs comparable x86
  - Spot and On-Demand capacity types for additional savings
  - Karpenter automatically selects the most cost-effective instance type from available options
- **Scaling**: Automatically scales based on pod requirements and consolidates underutilized nodes

#### 2. **High-Performance Computing Nodes** 
- **Instance Types**: AWS dedicated high-performance instances (c5, m5, r5 families)
- **Purpose**: Running compute-intensive AI/ML workloads
- **Features**: Optimized networking, enhanced storage performance

#### 3. **AWS Neuron Nodes**
- **Instance Types**: inf2, trn1 and trn2 instances
- **Purpose**: Optimized inference for large-scale language models
- **Benefits**: 
  - Up to 50% lower cost per inference compared to AWS dedicated instances
  - Pre-compiled models for optimal performance
  - Native int8 quantization support

:::code{language=bash showCopyAction=true}
# View available node pools and their configurations
kubectl get nodepools -o wide
:::

You're now ready to start your hands-on Telco research journey!

---

**[Continue to Docker Basics →](/30-docker-basics/)**
