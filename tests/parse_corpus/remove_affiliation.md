# **C3-Bench: A Context-Aware Change Captioning Benchmark** 

Jae-Woo Kim<sup>1</sup> , Hyeongbeom Kim<sup>1</sup> , and Ue-Hwan Kim<sup>1</sup><sup>_,_2</sup><sup>_⋆_</sup> 

> 1Gwangju Institute of Science and Technology, Gwangju, Republic of Korea 

> 2GIST InnoCORE AI-Nano Convergence Institute for Early Detection of Neurodegenerative Diseases, Gwangju Institute of Science and Technology, 61005 Gwangju, 

Republic of Korea 

`kjw01124@gm.gist.ac.kr, hbk08101@gm.gist.ac.kr, uehwan@gist.ac.kr` **Project Page:** `https://github.com/AutoCompSysLab/C3-Bench` 

**Abstract.** While Change Captioning systems have garnered substantial attention to respond to our evolving world, their true performance on _diverse real-world change contexts_ remains largely unexplored due to the lack of comprehensive evaluation frameworks. To fill this gap, we propose **C3-Bench** , a comprehensive benchmark for evaluating **C** ontext-aware **C** hange **C** aptioning. C3-Bench features: (1) 4,996 human-labeled image pairs of 51 real-world change contexts across four domains (e.g., natural scenes, remote sensing imagery, image editing, and anomalies), each with diverse, carefully curated scenarios derived from multiple change-centric communities; and (2) the first LLM-as-Judge evaluation framework in the change captioning task that measure fine-grained dimensions (e.g., correctness, specificity, fluency, and relevance), along with a novel reversibility metric exploring whether models understand changes with symmetric consistency. Based on C3-Bench, we benchmark 32 models—including 