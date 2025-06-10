# SWE-Flow: Synthesizing Software Engineering Data in a Test-Driven Manner

> Official implementation of the ICML 2025 paper: Synthesizing Software Engineering Data in a Test-Driven Manner



## ✨ Overview

<img src="./assets/figures/sweflow-framework.png" alt="SWE-Flow Framework" style="zoom:80%;" />

**SWE-Flow** is a data-synthesis framework that turns unit tests into fully-verifiable, incremental development tasks.
It constructs a Runtime Dependency Graph (RDG) to trace function interactions and automatically derives a step-by-step development schedule:

- Partial codebase for each step
- Unit tests that express the high-level requirement
- Minimal code patch needed to make the tests pass

With this pipeline we generated 16,061 training and 2,020 test instances from real-world GitHub projects, forming the **SWE-Flow** Dataset. Fine-tuning open models on this dataset yields significant gains on TDD-oriented coding tasks.


## 🔧 Installation

```bash
git clone https://github.com/Hambaobao/SWE-Flow.git
cd SWE-Flow
pip install -e .
```


## 📚 Documentation

- [Dataset Synthesis Pipeline](./docs/pipeline.md)



## 🤝 Contributing

Contributions are welcome! A detailed [CONTRIBUTING.md](./CONTRIBUTING.md) guideline will be added soon. Feel free to open issues or pull requests in the meantime.



## 📄 License

This repository is licensed under the **MIT** License. See [License](./LICENSE) for the full text.



## 📌 Citation

If you use SWE-Flow, please cite:
```bibtex

```



## 🙏 Acknowledgments

Work done during an internship at **Alibaba Qwen**.
We thank the Alibaba Qwen Team and the open-source community for the projects that enabled **SWE-Flow**.
