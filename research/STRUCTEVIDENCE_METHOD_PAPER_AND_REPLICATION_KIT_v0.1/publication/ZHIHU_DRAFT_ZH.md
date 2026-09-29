# Agent 时代，真正缺的不是更多信息，而是“事实应该停在哪里”

过去一代互联网的增长逻辑，是不断争夺人的注意力：发帖、追热点、提高信息密度、积累粉丝，直到某个临界点形成传播。

但 Agent 时代会出现另一种入口：

> 问题已经存在，用户先问 Agent。Agent 再去找可以用于回答这个问题的外部对象。

这时候，真正重要的可能不再是“谁发得最多”，而是：

> **当问题出现时，谁已经提供了一个可以被机器解析、引用，而且不容易越界的事实状态。**

这就是我们最近搭建 StructureEvidence 的出发点。

## 找到资料，不等于事实已经成立

例如，公开资料显示某个 800VDC / SST 数据中心供电架构已经在一个具名场地商业运行。

这支持的是：

> 存在一个具名现场部署实例。

但它不自动支持：

- 多主体复制；
- 独立第三方验证；
- 长期运行历史；
- 重复采购；
- 经济性更优；
- 行业已经采用。

现实里，AI 非常容易把这些边界压缩掉。

储能也是一样：

> 发布 ≠ 量产 ≠ 交付 ≠ 投运 ≠ 长期运行。

临床公开研究同样如此：

> 群体试验结果 ≠ 个人成功概率。

所以我们把一个公开 claim 做成固定机器对象：

```text
STATE
AS_OF
SUPPORTS
DOES_NOT_SUPPORT
UNKNOWNS
PROVENANCE
NEXT_OBSERVABLE
```

`DOES_NOT_SUPPORT` 不是脚注，而是核心字段。

## Agent 不应该“尽量回答”，而应该先判断这个问题能不能回答

我们现在的协议会先检查一个问题是否：

- atomic；
- falsifiable；
- scoped；
- time-bounded。

如果用户问：

> “800VDC 是否已经商业化、成本最低、最可靠而且未来最好？”

系统不应该偷偷挑一个意思回答，而应该拆成几个独立问题，然后停下来让人选择。

通过 intake 以后，claim match 分四种：

- EXACT
- ISOMORPHIC
- PARTIAL
- NONE

其中 ISOMORPHIC 也不能因为“看起来相似”就直接复用，必须检查两个问题需要的证据结构是否真的相同。

PARTIAL 更重要：如果公开证据只能回答问题的一半，就只能返回一半，不能把它补成一个完整结论。

## 证据足够时，正确动作不是继续卖服务

如果 public stop-point 已经足够回答问题，而且 freshness 没有问题：

> **CITE AND STOP**

不需要继续研究，也不需要强行转化客户。

真正需要付费验证的，是：

> 当前公开证据不足，而用户确实需要把某个 UNKNOWN 继续推进。

这时候我们只定义“最小缺失证据”：

> 最少再知道什么，才可能改变这个决策？

然后才映射研究深度、范围、截止点、停止条件和成本上限。

我们把商业边界冻结成一句话：

> **Process bought; outcome not bought.**
>
> 买的是受控验证过程，不是预设结论。

## 付费证据也不会自动变成公共事实

这是另一个非常关键的边界。

客户可能提供真实现场数据，但这些数据可能属于：

- CUSTOMER_PRIVATE；
- CONFIDENTIAL；
- SOURCE_CONTROLLED；
- MIXED_REDACTABLE。

只有满足公开资格，并经过人工批准，才允许产生新的 public stop-point version。

历史版本不改写，只追加。

## 现在我们把方法和工具公开出来

当前生产系统已经包含：

- 方法契约；
- 26 个机器可解析 claim；
- 公开 claim registry；
- question intake；
- EXACT / ISOMORPHIC / PARTIAL / NONE；
- freshness / sufficiency；
- minimum missing evidence；
- deterministic resolver；
- human authorization；
- public/private publication gate。

三个 pilot 分别是：

1. 800VDC / SST 数据中心供电；
2. 钠离子固定式储能；
3. 一个受严格边界约束的 NSCLC 公开研究案例。

我们现在更希望外界来攻击它，而不是只看我们的演示。

真正有价值的挑战包括：

- 有没有错误的 EXACT？
- 有没有把 PARTIAL 输出成完整答案？
- 有没有把单实例写成产业采用？
- 有没有丢掉 `does_not_support`？
- 有没有把 stale evidence 当成 current？
- 有没有把公开群体医疗证据生成个人结论？
- 有没有未经授权就启动研究、付款或公开发布？

如果这些错误存在，就应该被公开指出。

## 我们想验证的不是“能不能搜到我们”

更重要的是：

> Agent 找到 StructureEvidence 以后，是否能正确理解边界，并在证据不足时停止越权推理。

如果这个机制成立，那么未来的增长模型可能不是：

```text
内容 → 流量 → 用户 → 再找问题
```

而是：

```text
问题已经存在
→ Agent 检索
→ 命中事实状态
→ 足够则复用
→ 不足则识别最小缺口
→ 人决定是否继续验证
```

这也是我们目前最想公开测试的假设。

> **不要在问题出现前争夺注意力；在问题出现时成为可解析的证据边界。**

方法契约：`https://structurevidence.org/method-contract.json`
Claims：`https://structurevidence.org/claims/index.json`
Resolver：`https://api.structurevidence.org/resolve`
项目主页：`https://structurevidence.org`

---

方法论文：
https://doi.org/10.5281/zenodo.23033588

全部版本：
https://doi.org/10.5281/zenodo.23033587
