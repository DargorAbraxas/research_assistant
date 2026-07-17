The dataset is large enough to make those comparisons meaningful. We scraped 59,550 repositories with at least 1,000 GitHub stars, found CI/CD configurations in 34,225 repositories, and downloaded 127,559 workflow files spanning GitHub Actions, Travis CI, CircleCI, Jenkins, GitLab CI/CD, AppVeyor, and Azure Pipelines. This study is organized around three research questions: 

- 1) (RQ1) Which CI/CD anti-patterns dominate large-scale open-source workflows? 

- 2) (RQ2) How do stage usage and optimization features vary across languages and project domains? 

- 3) (RQ3) Which prompting strategy yields the most usable automated CI/CD recommendations? 

Figure 1 summarizes the full workflow, from repository collection and enrichment through anti-pattern detection, stage mining, and recommendation generation. Three findings stand out. First, routine operational debt is everywhere: across 75,201 workflow files, the anti-pattern detector reports 434,769 findings, with reliability issues alone accounting for 150,230 cases. Second, while build and test remain the dominant stages across 59,906 workflows, stage usage changes measurably across language ecosystems and repository domains. Third, for repository-level recommendations, few-shot prompting gives the best overall balance of coverage and machine-checkable validity, whereas iterative prompting shifts more of the output toward critical issues. Taken together, these results suggest that CI/CD governance benefits more from context-aware analysis than from a single universal checklist. 