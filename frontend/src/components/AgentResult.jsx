import {
  Check,
  CheckCircle2,
  Copy,
  ExternalLink,
  ShieldAlert,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { useState } from "react";

function formatOperation(operation) {
  return operation
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function AgentResult({ result }) {
  const [copied, setCopied] = useState(false);

  const isSuccess = result.success;
  const reliability = result.reliability;
  const paymentLink = result.result?.short_url;

  const copyLink = async () => {
    if (!paymentLink) {
      return;
    }

    try {
      await navigator.clipboard.writeText(paymentLink);
      setCopied(true);

      window.setTimeout(() => {
        setCopied(false);
      }, 1800);
    } catch {
      setCopied(false);
    }
  };

  return (
    <section
      className={`agent-result ${
        isSuccess ? "agent-result-success" : "agent-result-failure"
      }`}
    >
      <div className="result-header">
        <div className="result-status-icon">
          {isSuccess ? (
            <CheckCircle2 size={20} />
          ) : (
            <ShieldAlert size={20} />
          )}
        </div>

        <div className="result-heading">
          <span className="result-eyebrow">
            {isSuccess ? "OPERATION VERIFIED" : "ACTION NOT COMPLETED"}
          </span>

          <h2>
            {isSuccess
              ? formatOperation(result.operation)
              : result.status === "validation_failed"
                ? "Action blocked"
                : "Operation failed"}
          </h2>
        </div>

        <div
          className={`result-status ${
            isSuccess ? "result-status-success" : "result-status-failure"
          }`}
        >
          {isSuccess ? (
            <>
              <CheckCircle2 size={13} />
              Completed
            </>
          ) : (
            <>
              <XCircle size={13} />
              {result.status === "validation_failed" ? "Blocked" : "Failed"}
            </>
          )}
        </div>
      </div>

      {!isSuccess ? (
        <div className="failure-card">
          <div className="failure-icon">
            <ShieldAlert size={18} />
          </div>

          <div>
            <strong>
              {result.status === "validation_failed"
                ? "Safety check prevented the action"
                : "Razorpay operation could not be completed"}
            </strong>

            <p>{result.message || "No financial action was taken."}</p>

            <div className="failure-confirmation">
              <ShieldCheck size={14} />
              No unverified financial action was executed.
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="result-details">
            <div className="detail-item">
              <span>Operation</span>
              <strong>{formatOperation(result.operation)}</strong>
            </div>

            {result.result?.id && (
              <div className="detail-item">
                <span>Razorpay ID</span>
                <strong className="detail-mono">{result.result.id}</strong>
              </div>
            )}

            {result.result?.amount !== undefined && (
              <div className="detail-item">
                <span>Amount</span>
                <strong>
                  {result.result.currency === "INR" ? "₹" : ""}
                  {(result.result.amount / 100).toLocaleString("en-IN")}
                </strong>
              </div>
            )}

            {result.result?.status && (
              <div className="detail-item">
                <span>Status</span>
                <strong className="detail-status">
                  <span />
                  {result.result.status}
                </strong>
              </div>
            )}
          </div>

          {paymentLink && (
            <div className="payment-link-card">
              <div className="payment-link-heading">
                <div>
                  <span>PAYMENT LINK</span>
                  <strong>Ready to share with your customer</strong>
                </div>

                <ExternalLink size={17} />
              </div>

              <div className="payment-link-value">
                <span>{paymentLink}</span>

                <button type="button" onClick={copyLink}>
                  {copied ? <Check size={15} /> : <Copy size={15} />}
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {isSuccess && reliability && (
        <div className="reliability-card">
          <div className="reliability-card-header">
            <div>
              <span className="result-eyebrow">RELIABILITY</span>
              <strong>Verified against Razorpay response</strong>
            </div>

            <div className="reliability-score-large">
              {Math.round(reliability.reliability_score * 100)}%
            </div>
          </div>

          <div className="reliability-progress">
            <span
              style={{
                width: `${Math.max(
                  0,
                  Math.min(100, reliability.reliability_score * 100),
                )}%`,
              }}
            />
          </div>

          <div className="reliability-meta">
            <span>
              <ShieldCheck size={13} />
              {reliability.reliability_status.replaceAll("_", " ")}
            </span>

            <span>
              Confidence:{" "}
              <strong>
                {reliability.confidence_level}
              </strong>
            </span>
          </div>
        </div>
      )}

      <div className="result-footer">
        <span>
          <ShieldCheck size={13} />
          PayPilot verified the operation before reporting success.
        </span>
      </div>
    </section>
  );
}

export default AgentResult;