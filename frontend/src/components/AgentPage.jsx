import { useState } from "react";
import "./AgentPage.css";
import {
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Copy,
  ExternalLink,
  FileCheck2,
  Link2,
  Loader2,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  XCircle,
  Zap,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const QUICK_ACTIONS = [
  {
    label: "Create ₹500 payment link",
    icon: Link2,
    query: "Create a payment link for ₹500 for a test order",
  },
  {
    label: "Show recent payments",
    icon: RefreshCcw,
    query: "Show me the recent payments",
  },
  {
    label: "Refund a payment",
    icon: ArrowUpRight,
    query: "Refund payment pay_example123",
  },
];

const formatOperation = (operation) => {
  if (!operation) return "Unknown operation";

  return operation
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1)
    )
    .join(" ");
};

const formatAmount = (amount, currency = "INR") => {
  if (typeof amount !== "number") return "—";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount / 100);
};

function AgentPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const executeAgent = async (requestQuery = query) => {
    const trimmedQuery = requestQuery.trim();

    if (!trimmedQuery || loading) return;

    setQuery(trimmedQuery);
    setLoading(true);
    setResult(null);
    setError("");
    setCopied(false);

    try {
      const response = await fetch(`${API_URL}/agent/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: trimmedQuery,
        }),
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The agent returned an invalid response."
        );
      }

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "The agent request failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the AI Agent."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    executeAgent();
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      executeAgent();
    }
  };

  const handleQuickAction = (action) => {
    setQuery(action.query);
    executeAgent(action.query);
  };

  const copyPaymentLink = async (url) => {
    if (!url) return;

    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);

      window.setTimeout(() => {
        setCopied(false);
      }, 1800);
    } catch {
      setCopied(false);
    }
  };

  const paymentLink = result?.result?.short_url;
  const resultAmount = result?.result?.amount;
  const resultCurrency = result?.result?.currency;
  const resultDescription = result?.result?.description;
  const reliabilityScore = result?.reliability?.score;

  return (
    <div className="agent-page">
      <section className="agent-hero">
        <div className="agent-hero-orb agent-hero-orb-one" />
        <div className="agent-hero-orb agent-hero-orb-two" />

        <div className="agent-hero-content">
          <div className="agent-badge">
            <Sparkles size={12} />
            AI PAYMENT OPERATIONS
          </div>

          <h1>
            Operate payments
            <br />
            with <span>natural language.</span>
          </h1>

          <p>
            Tell PayPilot what you need to accomplish.
            The agent translates your request into a
            structured operation, validates it with
            deterministic guardrails, and executes it
            through Razorpay Test Mode.
          </p>
        </div>

        <div className="agent-trust-strip">
          <div>
            <ShieldCheck size={13} />
            Guardrails before execution
          </div>

          <div>
            <FileCheck2 size={13} />
            Reliability verification
          </div>

          <div>
            <Zap size={13} />
            Razorpay API integration
          </div>
        </div>
      </section>

      <section className="agent-workspace">
        <form
          className="agent-composer"
          onSubmit={handleSubmit}
        >
          <div className="composer-top">
            <div className="composer-icon">
              <Bot size={17} />
            </div>

            <div>
              <div className="composer-label">
                PAYMENT OPERATIONS AGENT
              </div>

              <div className="composer-hint">
                Describe the operation you want to perform
              </div>
            </div>
          </div>

          <textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="e.g. Create a payment link for ₹500 for a test order"
            aria-label="Describe a payment operation"
          />

          <div className="composer-footer">
            <div className="composer-safety">
              <ShieldCheck size={12} />
              Financial actions are validated before execution
            </div>

            <button
              className="execute-button"
              type="submit"
              disabled={!query.trim() || loading}
            >
              {loading ? (
                <>
                  <Loader2 size={13} className="spin" />
                  Executing...
                </>
              ) : (
                <>
                  Execute operation
                  <ArrowUpRight size={13} />
                </>
              )}
            </button>
          </div>
        </form>

        <div className="quick-actions">
          <span className="quick-actions-label">
            TRY AN EXAMPLE
          </span>

          <div className="quick-actions-list">
            {QUICK_ACTIONS.map((action) => {
              const Icon = action.icon;

              return (
                <button
                  className="quick-action"
                  type="button"
                  key={action.label}
                  onClick={() =>
                    handleQuickAction(action)
                  }
                  disabled={loading}
                >
                  <Icon size={12} />
                  {action.label}
                </button>
              );
            })}
          </div>
        </div>

        {loading && (
          <section className="agent-processing">
            <div className="processing-header">
              <div className="processing-pulse">
                <Bot size={17} />
              </div>

              <div>
                <strong>
                  Agent is executing your request
                </strong>

                <span>
                  Parsing, validating and contacting
                  Razorpay.
                </span>
              </div>
            </div>

            <div className="processing-steps">
              <div className="processing-step processing-step-active">
                <Sparkles size={11} />
                Understanding request
              </div>

              <div className="processing-step processing-step-active">
                <ShieldCheck size={11} />
                Running guardrails
              </div>

              <div className="processing-step processing-step-active">
                <Zap size={11} />
                Executing operation
              </div>
            </div>
          </section>
        )}

        {error && !loading && (
          <section className="agent-result agent-result-failure">
            <div className="result-header">
              <div className="result-status-icon">
                <XCircle size={19} />
              </div>

              <div className="result-heading">
                <span className="result-eyebrow">
                  OPERATION FAILED
                </span>

                <h2>Unable to execute request</h2>
              </div>

              <span className="result-status result-status-failure">
                <XCircle size={11} />
                Failed
              </span>
            </div>

            <div className="failure-card">
              <div className="failure-icon">
                <XCircle size={16} />
              </div>

              <div>
                <strong>Request could not be completed</strong>
                <p>{error}</p>
              </div>
            </div>
          </section>
        )}

        {result && !loading && (
          <section
            className={`agent-result ${
              result.success
                ? "agent-result-success"
                : "agent-result-failure"
            }`}
          >
            <div className="result-header">
              <div className="result-status-icon">
                {result.success ? (
                  <CheckCircle2 size={19} />
                ) : (
                  <XCircle size={19} />
                )}
              </div>

              <div className="result-heading">
                <span className="result-eyebrow">
                  AGENT RESULT
                </span>

                <h2>
                  {formatOperation(result.operation)}
                </h2>
              </div>

              <span
                className={`result-status ${
                  result.success
                    ? "result-status-success"
                    : "result-status-failure"
                }`}
              >
                {result.success ? (
                  <CheckCircle2 size={11} />
                ) : (
                  <XCircle size={11} />
                )}

                {result.status?.replaceAll("_", " ")}
              </span>
            </div>

            {result.success ? (
              <>
                <div className="result-details">
                  <div className="detail-item">
                    <span>Operation</span>
                    <strong>
                      {formatOperation(
                        result.operation
                      )}
                    </strong>
                  </div>

                  <div className="detail-item">
                    <span>Amount</span>
                    <strong>
                      {formatAmount(
                        resultAmount,
                        resultCurrency
                      )}
                    </strong>
                  </div>

                  <div className="detail-item">
                    <span>Status</span>
                    <strong className="detail-status">
                      <span />
                      {result.result?.status || "Completed"}
                    </strong>
                  </div>

                  <div className="detail-item">
                    <span>Reliability</span>
                    <strong>
                      {typeof reliabilityScore ===
                      "number"
                        ? `${Math.round(
                            reliabilityScore * 100
                          )}%`
                        : "Verified"}
                    </strong>
                  </div>
                </div>

                {resultDescription && (
                  <div className="payment-link-card">
                    <div className="payment-link-heading">
                      <div>
                        <span>PAYMENT LINK CREATED</span>
                        <strong>
                          {resultDescription}
                        </strong>
                      </div>

                      <Link2 size={15} />
                    </div>

                    {paymentLink && (
                      <div className="payment-link-value">
                        <span>{paymentLink}</span>

                        <button
                          type="button"
                          onClick={() =>
                            copyPaymentLink(paymentLink)
                          }
                        >
                          <Copy size={10} />
                          {copied ? "Copied" : "Copy"}
                        </button>

                        <a
                          className="operation-icon-button"
                          href={paymentLink}
                          target="_blank"
                          rel="noreferrer"
                          aria-label="Open payment link"
                        >
                          <ExternalLink size={11} />
                        </a>
                      </div>
                    )}
                  </div>
                )}

                <div className="reliability-card">
                  <div className="reliability-card-header">
                    <div>
                      <span className="result-eyebrow">
                        RELIABILITY VERIFICATION
                      </span>

                      <strong>
                        Result verified after execution
                      </strong>
                    </div>

                    <div className="reliability-score-large">
                      {typeof reliabilityScore ===
                      "number"
                        ? `${Math.round(
                            reliabilityScore * 100
                          )}%`
                        : "—"}
                    </div>
                  </div>

                  {typeof reliabilityScore ===
                    "number" && (
                    <div className="reliability-progress">
                      <span
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(
                              100,
                              reliabilityScore * 100
                            )
                          )}%`,
                        }}
                      />
                    </div>
                  )}

                  <div className="reliability-meta">
                    <span>
                      <ShieldCheck size={11} />
                      {result.reliability
                        ?.classification ||
                        "verified"}
                    </span>

                    <strong>
                      High confidence
                    </strong>
                  </div>
                </div>
              </>
            ) : (
              <div className="failure-card">
                <div className="failure-icon">
                  <XCircle size={16} />
                </div>

                <div>
                  <strong>
                    Operation was not executed
                  </strong>

                  <p>
                    {result.message ||
                      "The request failed validation or could not be completed."}
                  </p>

                  {result.status ===
                    "validation_failed" && (
                    <div className="failure-confirmation">
                      <ShieldCheck size={11} />
                      Guardrails prevented the operation
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="result-footer">
              <ShieldCheck size={11} />
              PayPilot records this operation in the
              activity log.
            </div>
          </section>
        )}
      </section>
    </div>
  );
}

export default AgentPage;