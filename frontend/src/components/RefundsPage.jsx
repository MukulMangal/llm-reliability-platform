import {
  AlertTriangle,
  CheckCircle2,
  RefreshCcw,
  RotateCcw,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatAmount(amount, currency = "INR") {
  if (typeof amount !== "number") {
    return "—";
  }

  if (currency === "INR") {
    return `₹${(amount / 100).toLocaleString("en-IN")}`;
  }

  return `${currency} ${(amount / 100).toLocaleString()}`;
}

function formatDate(timestamp) {
  if (!timestamp) {
    return "—";
  }

  return new Date(timestamp * 1000).toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    },
  );
}

export default function RefundsPage() {
  const [refunds, setRefunds] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const [paymentId, setPaymentId] = useState("");
  const [amount, setAmount] = useState("");
  const [refunding, setRefunding] = useState(false);
  const [refundMessage, setRefundMessage] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      const [refundResponse, paymentResponse] =
        await Promise.all([
          fetch(`${API_URL}/refunds/?count=100`),
          fetch(`${API_URL}/payments/?count=100`),
        ]);

      if (!refundResponse.ok || !paymentResponse.ok) {
        throw new Error("Unable to load refund data.");
      }

      const [refundData, paymentData] =
        await Promise.all([
          refundResponse.json(),
          paymentResponse.json(),
        ]);

      setRefunds(
        Array.isArray(refundData.refunds)
          ? refundData.refunds
          : [],
      );

      setPayments(
        Array.isArray(paymentData.payments)
          ? paymentData.payments
          : [],
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load refund data.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const capturedPayments = useMemo(
    () =>
      payments.filter(
        (payment) => payment.status === "captured",
      ),
    [payments],
  );

  const filteredRefunds = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return refunds;
    }

    return refunds.filter((refund) =>
      [
        refund.id,
        refund.payment_id,
        refund.status,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query),
        ),
    );
  }, [refunds, search]);

  const selectedPayment = payments.find(
    (payment) => payment.id === paymentId,
  );

  const refundAmount = amount
    ? Math.round(Number(amount) * 100)
    : null;

  const amountExceedsPayment =
    selectedPayment &&
    refundAmount !== null &&
    refundAmount > selectedPayment.amount;

  const submitRefund = async (event) => {
    event.preventDefault();

    setRefundMessage(null);

    if (!paymentId.trim()) {
      setRefundMessage({
        type: "error",
        text: "Enter a valid payment ID.",
      });
      return;
    }

    if (
      selectedPayment &&
      selectedPayment.status !== "captured"
    ) {
      setRefundMessage({
        type: "error",
        text: "Refunds are only allowed for captured payments.",
      });
      return;
    }

    if (
      refundAmount !== null &&
      (!Number.isFinite(refundAmount) || refundAmount <= 0)
    ) {
      setRefundMessage({
        type: "error",
        text: "Enter a valid refund amount.",
      });
      return;
    }

    if (amountExceedsPayment) {
      setRefundMessage({
        type: "error",
        text: "Refund amount cannot exceed the captured payment amount.",
      });
      return;
    }

    setRefunding(true);

    try {
      const response = await fetch(`${API_URL}/refunds/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          payment_id: paymentId.trim(),
          amount:
            refundAmount === null ? null : refundAmount,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to process refund.",
        );
      }

      setRefundMessage({
        type: "success",
        text: "Refund processed successfully.",
      });

      setPaymentId("");
      setAmount("");

      await loadData();
    } catch (err) {
      setRefundMessage({
        type: "error",
        text:
          err instanceof Error
            ? err.message
            : "Unable to process refund.",
      });
    } finally {
      setRefunding(false);
    }
  };

  return (
    <div className="operations-page">
      <section className="operations-heading">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" />
            REFUND OPERATIONS
          </div>

          <h1>Refunds</h1>

          <p>
            Review and safely process refunds for captured
            payments.
          </p>
        </div>

        <button
          className="operations-refresh-button"
          type="button"
          onClick={loadData}
          disabled={loading}
        >
          <RefreshCcw size={15} />
          Refresh
        </button>
      </section>

      <section className="refund-safety-banner">
        <div className="refund-safety-icon">
          <ShieldCheck size={19} />
        </div>

        <div>
          <strong>Protected financial operation</strong>
          <span>
            Refunds are validated before reaching Razorpay.
            Only captured payments can be refunded, and partial
            refunds cannot exceed the captured amount.
          </span>
        </div>
      </section>

      <section className="refund-layout">
        <article className="panel refund-form-panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">
                Process a refund
              </div>
              <div className="panel-subtitle">
                Deterministic validation before execution
              </div>
            </div>

            <RotateCcw
              size={18}
              className="panel-header-icon"
            />
          </div>

          <form
            className="refund-form"
            onSubmit={submitRefund}
          >
            <label className="operation-field">
              <span>Payment ID</span>

              <input
                type="text"
                placeholder="pay_..."
                value={paymentId}
                onChange={(event) => {
                  setPaymentId(event.target.value);
                  setRefundMessage(null);
                }}
              />
            </label>

            {selectedPayment && (
              <div className="refund-payment-preview">
                <div>
                  <span>Payment status</span>
                  <strong>
                    {selectedPayment.status}
                  </strong>
                </div>

                <div>
                  <span>Captured amount</span>
                  <strong>
                    {formatAmount(
                      selectedPayment.amount,
                      selectedPayment.currency,
                    )}
                  </strong>
                </div>
              </div>
            )}

            <label className="operation-field">
              <span>
                Refund amount
                <small>Leave empty for a full refund</small>
              </span>

              <div className="operation-input-wrap">
                <span>₹</span>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  placeholder={
                    selectedPayment
                      ? (
                          selectedPayment.amount / 100
                        ).toString()
                      : "500"
                  }
                  value={amount}
                  onChange={(event) => {
                    setAmount(event.target.value);
                    setRefundMessage(null);
                  }}
                />
              </div>
            </label>

            {amountExceedsPayment && (
              <div className="operation-form-error">
                <AlertTriangle size={15} />
                Refund amount exceeds the captured payment.
              </div>
            )}

            {refundMessage && (
              <div
                className={`refund-message refund-message-${refundMessage.type}`}
              >
                {refundMessage.type === "success" ? (
                  <CheckCircle2 size={15} />
                ) : (
                  <AlertTriangle size={15} />
                )}
                {refundMessage.text}
              </div>
            )}

            <button
              className="operations-primary-button refund-submit"
              type="submit"
              disabled={refunding || amountExceedsPayment}
            >
              {refunding ? (
                <>
                  <span className="button-spinner" />
                  Processing...
                </>
              ) : (
                <>
                  <RotateCcw size={15} />
                  Process refund
                </>
              )}
            </button>
          </form>
        </article>

        <article className="panel refund-context-panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">
                Refund eligibility
              </div>
              <div className="panel-subtitle">
                Current payment state
              </div>
            </div>
          </div>

          <div className="refund-check-list">
            <div>
              <CheckCircle2 size={16} />
              <span>Payment must exist</span>
            </div>

            <div>
              <CheckCircle2 size={16} />
              <span>Payment must be captured</span>
            </div>

            <div>
              <CheckCircle2 size={16} />
              <span>
                Refund amount must be valid
              </span>
            </div>

            <div>
              <CheckCircle2 size={16} />
              <span>
                Partial refund cannot exceed payment
              </span>
            </div>
          </div>

          <div className="refund-eligible-count">
            <strong>{capturedPayments.length}</strong>
            <span>captured payments currently eligible</span>
          </div>
        </article>
      </section>

      <article className="panel operations-table-panel">
        <div className="panel-header">
          <div>
            <div className="panel-title">
              Refund history
            </div>
            <div className="panel-subtitle">
              Live data from Razorpay Test Mode
            </div>
          </div>

          <div className="operations-search">
            <Search size={14} />
            <input
              type="search"
              placeholder="Search refunds"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </div>
        </div>

        {loading ? (
          <div className="operations-state">
            <div className="operations-spinner" />
            <strong>Loading refunds</strong>
            <span>
              Fetching the latest refund information.
            </span>
          </div>
        ) : error ? (
          <div className="operations-state operations-state-error">
            <div className="operations-state-icon">
              <RefreshCcw size={18} />
            </div>
            <strong>Unable to load refunds</strong>
            <span>{error}</span>
            <button
              className="operations-state-button"
              type="button"
              onClick={loadData}
            >
              Try again
            </button>
          </div>
        ) : filteredRefunds.length === 0 ? (
          <div className="operations-state">
            <div className="operations-state-icon">
              <RotateCcw size={20} />
            </div>

            <strong>No refunds yet</strong>

            <span>
              Refunds will appear here after a successful
              refund operation.
            </span>
          </div>
        ) : (
          <div className="operations-table-wrapper">
            <div className="operations-table-header refund-columns">
              <span>Refund</span>
              <span>Payment</span>
              <span>Amount</span>
              <span>Status</span>
              <span>Created</span>
            </div>

            {filteredRefunds.map((refund) => (
              <div
                className="operations-table-row refund-columns"
                key={refund.id}
              >
                <div className="operation-primary">
                  <div className="operation-row-icon">
                    <RotateCcw size={14} />
                  </div>

                  <div>
                    <strong>{refund.id}</strong>
                    <span>
                      {refund.currency || "INR"}
                    </span>
                  </div>
                </div>

                <span className="operation-secondary">
                  {refund.payment_id || "—"}
                </span>

                <strong className="operation-amount">
                  {formatAmount(
                    refund.amount,
                    refund.currency,
                  )}
                </strong>

                <span
                  className={`payment-status payment-status-${String(
                    refund.status || "unknown",
                  ).toLowerCase()}`}
                >
                  <span />
                  {refund.status || "Unknown"}
                </span>

                <span className="operation-secondary">
                  {formatDate(refund.created_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </article>
    </div>
  );
}