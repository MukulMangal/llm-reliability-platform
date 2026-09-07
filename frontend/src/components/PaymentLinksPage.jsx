import {
  Check,
  Copy,
  ExternalLink,
  Link2,
  Plus,
  RefreshCcw,
  Search,
  X,
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

export default function PaymentLinksPage() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");

  const loadLinks = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/payment-links/?count=100`,
      );

      if (!response.ok) {
        throw new Error("Unable to load payment links.");
      }

      const data = await response.json();

      setLinks(
        Array.isArray(data.payment_links)
          ? data.payment_links
          : [],
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load payment links.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLinks();
  }, []);

  const filteredLinks = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return links;
    }

    return links.filter((link) =>
      [
        link.id,
        link.description,
        link.status,
        link.short_url,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query),
        ),
    );
  }, [links, search]);

  const copyLink = async (link) => {
    if (!link.short_url) {
      return;
    }

    try {
      await navigator.clipboard.writeText(link.short_url);
      setCopiedId(link.id);

      window.setTimeout(() => {
        setCopiedId(null);
      }, 1800);
    } catch {
      // Clipboard availability varies by browser context.
    }
  };

  const createLink = async (event) => {
    event.preventDefault();

    setCreateError("");

    const numericAmount = Number(amount);

    if (!numericAmount || numericAmount <= 0) {
      setCreateError("Enter a valid amount.");
      return;
    }

    if (!description.trim()) {
      setCreateError("Enter a description.");
      return;
    }

    setCreating(true);

    try {
      const response = await fetch(
        `${API_URL}/payment-links/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount: Math.round(numericAmount * 100),
            description: description.trim(),
            currency: "INR",
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create payment link.",
        );
      }

      setAmount("");
      setDescription("");
      setShowCreate(false);

      await loadLinks();
    } catch (err) {
      setCreateError(
        err instanceof Error
          ? err.message
          : "Unable to create payment link.",
      );
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="operations-page">
      <section className="operations-heading">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" />
            PAYMENT COLLECTION
          </div>

          <h1>Payment Links</h1>

          <p>
            Create and manage shareable Razorpay payment links.
          </p>
        </div>

        <div className="operations-heading-actions">
          <button
            className="operations-refresh-button"
            type="button"
            onClick={loadLinks}
            disabled={loading}
          >
            <RefreshCcw size={15} />
            Refresh
          </button>

          <button
            className="operations-primary-button"
            type="button"
            onClick={() => {
              setCreateError("");
              setShowCreate(true);
            }}
          >
            <Plus size={16} />
            Create link
          </button>
        </div>
      </section>

      <section className="operations-stats">
        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <Link2 size={17} />
          </div>
          <span>Total links</span>
          <strong>{links.length}</strong>
        </article>

        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <Check size={17} />
          </div>
          <span>Active links</span>
          <strong>
            {
              links.filter(
                (link) => link.status === "created",
              ).length
            }
          </strong>
        </article>

        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <Link2 size={17} />
          </div>
          <span>Collected</span>
          <strong>
            {formatAmount(
              links.reduce(
                (total, link) =>
                  total + (link.amount_paid || 0),
                0,
              ),
            )}
          </strong>
        </article>
      </section>

      <article className="panel operations-table-panel">
        <div className="panel-header">
          <div>
            <div className="panel-title">Your payment links</div>
            <div className="panel-subtitle">
              Live data from Razorpay Test Mode
            </div>
          </div>

          <div className="operations-search">
            <Search size={14} />
            <input
              type="search"
              placeholder="Search links"
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
            <strong>Loading payment links</strong>
            <span>
              Fetching your latest Razorpay payment links.
            </span>
          </div>
        ) : error ? (
          <div className="operations-state operations-state-error">
            <div className="operations-state-icon">
              <RefreshCcw size={18} />
            </div>
            <strong>Unable to load payment links</strong>
            <span>{error}</span>
            <button
              className="operations-state-button"
              type="button"
              onClick={loadLinks}
            >
              Try again
            </button>
          </div>
        ) : filteredLinks.length === 0 ? (
          <div className="operations-state">
            <div className="operations-state-icon">
              <Link2 size={20} />
            </div>

            <strong>
              {links.length === 0
                ? "No payment links yet"
                : "No matching links"}
            </strong>

            <span>
              {links.length === 0
                ? "Create your first payment link to start collecting payments."
                : "Try a different search term."}
            </span>

            {links.length === 0 && (
              <button
                className="operations-state-button"
                type="button"
                onClick={() => setShowCreate(true)}
              >
                <Plus size={14} />
                Create payment link
              </button>
            )}
          </div>
        ) : (
          <div className="operations-table-wrapper">
            <div className="operations-table-header payment-link-columns">
              <span>Payment link</span>
              <span>Amount</span>
              <span>Collected</span>
              <span>Status</span>
              <span>Created</span>
              <span />
            </div>

            {filteredLinks.map((link) => (
              <div
                className="operations-table-row payment-link-columns"
                key={link.id}
              >
                <div className="operation-primary">
                  <div className="operation-row-icon operation-link-icon">
                    <Link2 size={14} />
                  </div>

                  <div>
                    <strong>
                      {link.description || "Payment link"}
                    </strong>
                    <span>{link.id}</span>
                  </div>
                </div>

                <strong className="operation-amount">
                  {formatAmount(
                    link.amount,
                    link.currency,
                  )}
                </strong>

                <span className="operation-secondary">
                  {formatAmount(
                    link.amount_paid,
                    link.currency,
                  )}
                </span>

                <span
                  className={`payment-status payment-status-${String(
                    link.status || "unknown",
                  ).toLowerCase()}`}
                >
                  <span />
                  {link.status || "Unknown"}
                </span>

                <span className="operation-secondary">
                  {formatDate(link.created_at)}
                </span>

                <div className="operation-actions">
                  <button
                    className="operation-icon-button"
                    type="button"
                    aria-label="Copy payment link"
                    onClick={() => copyLink(link)}
                  >
                    {copiedId === link.id ? (
                      <Check size={14} />
                    ) : (
                      <Copy size={14} />
                    )}
                  </button>

                  {link.short_url && (
                    <a
                      className="operation-icon-button"
                      href={link.short_url}
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Open payment link"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </article>

      {showCreate && (
        <div
          className="operation-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShowCreate(false);
            }
          }}
        >
          <div
            className="operation-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-payment-link-title"
          >
            <div className="operation-modal-header">
              <div>
                <div className="eyebrow">
                  <span className="eyebrow-line" />
                  RAZORPAY TEST MODE
                </div>

                <h2 id="create-payment-link-title">
                  Create payment link
                </h2>

                <p>
                  Generate a shareable link directly through
                  Razorpay.
                </p>
              </div>

              <button
                className="operation-modal-close"
                type="button"
                aria-label="Close"
                onClick={() => setShowCreate(false)}
              >
                <X size={17} />
              </button>
            </div>

            <form onSubmit={createLink}>
              <label className="operation-field">
                <span>Amount</span>

                <div className="operation-input-wrap">
                  <span>₹</span>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    placeholder="500"
                    value={amount}
                    onChange={(event) =>
                      setAmount(event.target.value)
                    }
                  />
                </div>
              </label>

              <label className="operation-field">
                <span>Description</span>

                <input
                  type="text"
                  maxLength={255}
                  placeholder="Test order"
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                />
              </label>

              {createError && (
                <div className="operation-form-error">
                  {createError}
                </div>
              )}

              <button
                className="operations-primary-button operation-submit-button"
                type="submit"
                disabled={creating}
              >
                {creating ? (
                  <>
                    <span className="button-spinner" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={16} />
                    Create payment link
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}