import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Shared markdown renderer used wherever the agent outputs text.
 * Supports headings, bold/italic, lists, tables, code blocks, and links.
 */
export default function Markdown({ children, className = "" }) {
  if (!children) return null;

  return (
    <div className={`md-body ${className}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Open external links in a new tab
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noopener noreferrer" />
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
