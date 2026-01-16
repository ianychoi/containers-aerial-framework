#!/usr/bin/env python3
import os
import sys
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf

# Create results directory
os.makedirs("/app/results", exist_ok=True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import sionna
    print(f"🔬 Sionna {sionna.__version__} experiment started")
except ImportError:
    print("❌ Sionna installation required: pip install sionna")
    exit(1)

from sionna.sys import PHYAbstraction, InnerLoopLinkAdaptation
from sionna.phy import config
from sionna.phy.utils import db_to_lin

# Sionna configuration
config.precision = 'single'
config.seed = 42

def load_config(path):
    """Load experiment configuration file"""
    with open(path) as f:
        return yaml.safe_load(f)

def run_phy_experiment(config):
    """Run PHY Abstraction experiment"""
    print(f"=== {config['experiment_id']} experiment ===")
    
    # Initialize PHY Abstraction and Link Adaptation
    phy_abs = PHYAbstraction()
    illa = InnerLoopLinkAdaptation(phy_abs, config['bler_target'])
    
    # Lists to store experiment results
    all_tbler = []
    all_throughput = []
    
    print(f"📊 Running {config['num_experiments']} experiments...")
    
    for exp in range(config['num_experiments']):
        # Generate SINR grid (random channel conditions)
        sinr_db = tf.random.uniform(
            [1, 1, config['num_ut'], 1],
            config['sinr_range'][0], 
            config['sinr_range'][1]
        ) + tf.random.normal(
            [config['num_sym'], config['num_sc'], config['num_ut'], 1], 
            stddev=2.0
        )
        sinr = db_to_lin(sinr_db)
        
        # MCS selection (Link Adaptation)
        mcs_index = illa(sinr=sinr, mcs_table_index=config['mcs_table_index'])
        
        # Perform PHY Abstraction
        num_decoded_bits, harq_feedback, sinr_eff, bler, tbler = phy_abs(
            mcs_index, 
            sinr=sinr, 
            mcs_table_index=config['mcs_table_index'],
            mcs_category=config['mcs_category']
        )
        
        # Collect results
        all_tbler.append(tbler.numpy().mean())
        all_throughput.append(num_decoded_bits.numpy().sum())
        
        if (exp + 1) % 5 == 0:
            print(f"  Progress: {exp + 1}/{config['num_experiments']}")
    
    # Calculate statistics
    results = {
        'tbler_mean': np.mean(all_tbler),
        'throughput_mean': np.mean(all_throughput),
        'tbler_std': np.std(all_tbler),
        'harq_nack_rate': 1 - np.mean(harq_feedback.numpy())
    }
    
    # Save results
    np.savez(f"results/{config['experiment_id']}.npz", **results)
    
    # Print results
    print(f"\n📈 Experiment results:")
    print(f"  TBLER: {results['tbler_mean']:.3f} ± {results['tbler_std']:.3f}")
    print(f"  Throughput: {results['throughput_mean']/1024:.1f} kbit")
    print(f"  HARQ NACK rate: {results['harq_nack_rate']:.3f}")
    
    # Visualize results
    create_plots(config, all_tbler, results)
    
    return results

def create_plots(config, all_tbler, results):
    """Visualize experiment results"""
    plt.figure(figsize=(12, 4))
    
    # TBLER distribution histogram
    plt.subplot(121)
    plt.hist(all_tbler, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(config['bler_target'], color='red', linestyle='--', 
                label=f'Target BLER: {config["bler_target"]}')
    plt.xlabel('TBLER')
    plt.ylabel('Frequency')
    plt.title('TBLER Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Summary bar chart
    plt.subplot(122)
    metrics = ['TBLER', 'Thuroughput (kbit)', 'NACK rate']
    values = [
        results['tbler_mean'], 
        results['throughput_mean']/1024, 
        results['harq_nack_rate']
    ]
    
    bars = plt.bar(metrics, values, color=['lightcoral', 'lightgreen', 'lightsalmon'])
    plt.title(f'{config["experiment_id"]} Summary')
    plt.xticks(rotation=45)
    
    # Display values on top of bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"results/{config['experiment_id']}.png", 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Graph saved: results/{config['experiment_id']}.png")

if __name__ == "__main__":
    # Configuration file path (default: baseline.yaml)
    config_file = sys.argv[1] if len(sys.argv) > 1 else "configs/baseline.yaml"
    
    try:
        config = load_config(config_file)
        results = run_phy_experiment(config)
        print("\n🏆 Experiment completed!")
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        exit(1)
    except Exception as e:
        print(f"❌ Error during experiment: {e}")
        exit(1)
