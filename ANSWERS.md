# Ticket Classification Questions

The following questions were answered based on the `1. Clustering.ipynb` and `2. Classification.ipynb` notebooks.

---

## 1. About the classes' performance

After exploring the tickets, I obtained the classes by running an HDBSCAN model -- a clustering technique -- on the ticket embeddings generated with a local embedding model. Then, I obtained a short description as well as keywords for each cluster through a local LLM. Based on the clusters' descriptions, keywords, and elements, I rearranged a smaller set of clusters into meaningful classes. Therefore, the classes were not chosen arbitrarily; they were discovered. Then, I used these clusters as labels for a multinomial logistic regression -- a classification model.

Because the target classes originated from an unsupervised clustering model, standard cross-validation metrics merely confirm alignment with the initial cluster assignments rather than ground truth. Consequently, rigorous evaluation requires human validation. To execute this, we could surface the classifier's outputs as recommendations and ask the support team to evaluate their accuracy. Once we collect a statistically meaningful sample of human ratings, we can calculate the classifier's actual Macro F1-score. Furthermore, we can configure an automated alert to trigger if the Macro F1-score drops below a designated threshold, while establishing a process to periodically re-cluster as new ticket volume grows.

---

## 2. Monitoring

- Macro F1-Score Alerts: Primary metric to track performance degradation against established baselines.
- Time-Series Tracking: Continuous evaluation of input features to detect data leakage and distribution shifts.
- Out-of-Scope Frequency: Monitoring rate variations in tickets assigned to the default Other category.
- Human Feedback Discrepancies: Tracking error rates derived from support team evaluations (qualifications).

---

## 3. Retraining

Full model retraining should be triggered whenever key metrics in the monitoring phase degrade or cross pre-defined alert thresholds. Although on-demand retraining (online learning) is an architectural option, it introduces operational complexity and carries a high risk of model drift or performance degradation.

## 4. Semi-supervising learning

The proposed solution closely mirrors a semi-supervised workflow. Given a subset of verified, human-labeled tickets, we can directly incorporate these ground-truth labels post-clustering to refine class boundaries before training the classification model.