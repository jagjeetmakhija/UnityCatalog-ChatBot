import React, { useState, useRef, useEffect } from 'react';
import { Send, Database, Users, Shield, CheckCircle, AlertCircle, Loader, Settings, Terminal } from 'lucide-react';

const UnityCatalogChatbot = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Unity Catalog assistant. I can help you create catalogs, schemas, tables, set permissions, and manage your data governance. What would you like to do?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLog, setActionLog] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Parse user intent and extract parameters
  const parseIntent = async (userMessage) => {
    const lowerMsg = userMessage.toLowerCase();
    
    // Define intent patterns
    const intents = {
      createCatalog: /create\s+(a\s+)?catalog\s+(?:named\s+)?["']?(\w+)["']?/i,
      createSchema: /create\s+(a\s+)?schema\s+(?:named\s+)?["']?(\w+\.?\w*)["']?/i,
      createTable: /create\s+(a\s+)?table\s+(?:named\s+)?["']?([\w.]+)["']?/i,
      grantPermission: /grant\s+(\w+)\s+(?:permission|access|privileges?)\s+(?:on\s+)?["']?([\w.]+)["']?\s+to\s+(?:user\s+)?["']?(\w+)["']?/i,
      revokePermission: /revoke\s+(\w+)\s+(?:permission|access|privileges?)\s+(?:on\s+)?["']?([\w.]+)["']?\s+from\s+(?:user\s+)?["']?(\w+)["']?/i,
      listCatalogs: /list\s+(all\s+)?catalogs?/i,
      listSchemas: /list\s+schemas?\s+(?:in\s+)?["']?(\w+)["']?/i,
      showPermissions: /show\s+permissions?\s+(?:for\s+)?["']?([\w.]+)["']?/i,
      setOwner: /set\s+owner\s+(?:of\s+)?["']?([\w.]+)["']?\s+to\s+["']?(\w+)["']?/i,
    };

    // Match intent
    for (const [intent, pattern] of Object.entries(intents)) {
      const match = userMessage.match(pattern);
      if (match) {
        return { intent, params: match.slice(1) };
      }
    }

    // Use Claude API for complex queries
    return await analyzeWithClaude(userMessage);
  };

  // Simulate API call to Claude for intent analysis
  const analyzeWithClaude = async (message) => {
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1000,
          messages: [{
            role: 'user',
            content: `Analyze this Unity Catalog request and extract the intent and parameters as JSON:
"${message}"

Possible intents: createCatalog, createSchema, createTable, grantPermission, revokePermission, listCatalogs, listSchemas, showPermissions, setOwner, complex, help

Return ONLY a JSON object with "intent" and "params" fields. For example:
{"intent": "createCatalog", "params": {"name": "sales_catalog"}}
{"intent": "grantPermission", "params": {"privilege": "SELECT", "object": "sales.customers", "principal": "data_analyst"}}
{"intent": "help", "params": {}}`
          }]
        })
      });

      const data = await response.json();
      const textResponse = data.content.find(c => c.type === 'text')?.text || '';
      
      // Extract JSON from response
      const jsonMatch = textResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Claude API error:', error);
    }

    return { intent: 'help', params: {} };
  };

  // Execute Unity Catalog operations
  const executeOperation = async (intent, params) => {
    const operations = {
      createCatalog: async (p) => {
        const catalogName = p[0] || p.name;
        return {
          sql: `CREATE CATALOG IF NOT EXISTS ${catalogName}`,
          message: `Created catalog '${catalogName}' successfully.`,
          action: { type: 'create', object: 'catalog', name: catalogName }
        };
      },
      
      createSchema: async (p) => {
        const schemaPath = p[0] || p.name;
        return {
          sql: `CREATE SCHEMA IF NOT EXISTS ${schemaPath}`,
          message: `Created schema '${schemaPath}' successfully.`,
          action: { type: 'create', object: 'schema', name: schemaPath }
        };
      },
      
      createTable: async (p) => {
        const tablePath = p[0] || p.name;
        return {
          sql: `CREATE TABLE IF NOT EXISTS ${tablePath} (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  data STRING
) USING DELTA`,
          message: `Created table '${tablePath}' with default schema. You can modify the schema as needed.`,
          action: { type: 'create', object: 'table', name: tablePath }
        };
      },
      
      grantPermission: async (p) => {
        const privilege = p[0] || p.privilege;
        const object = p[1] || p.object;
        const principal = p[2] || p.principal;
        return {
          sql: `GRANT ${privilege.toUpperCase()} ON ${object} TO \`${principal}\``,
          message: `Granted ${privilege} permission on '${object}' to user '${principal}'.`,
          action: { type: 'grant', privilege, object, principal }
        };
      },
      
      revokePermission: async (p) => {
        const privilege = p[0] || p.privilege;
        const object = p[1] || p.object;
        const principal = p[2] || p.principal;
        return {
          sql: `REVOKE ${privilege.toUpperCase()} ON ${object} FROM \`${principal}\``,
          message: `Revoked ${privilege} permission on '${object}' from user '${principal}'.`,
          action: { type: 'revoke', privilege, object, principal }
        };
      },
      
      listCatalogs: async () => {
        return {
          sql: `SHOW CATALOGS`,
          message: `Here are the available catalogs. Run the SQL query to see the full list.`,
          action: { type: 'list', object: 'catalogs' }
        };
      },
      
      listSchemas: async (p) => {
        const catalog = p[0] || p.catalog;
        return {
          sql: `SHOW SCHEMAS IN ${catalog}`,
          message: `Here are the schemas in catalog '${catalog}'.`,
          action: { type: 'list', object: 'schemas', catalog }
        };
      },
      
      showPermissions: async (p) => {
        const object = p[0] || p.object;
        return {
          sql: `SHOW GRANTS ON ${object}`,
          message: `Here are the current permissions for '${object}'.`,
          action: { type: 'show', object: 'permissions', target: object }
        };
      },
      
      setOwner: async (p) => {
        const object = p[0] || p.object;
        const owner = p[1] || p.owner;
        return {
          sql: `ALTER ${object.includes('.') ? 'TABLE' : 'CATALOG'} ${object} OWNER TO \`${owner}\``,
          message: `Set owner of '${object}' to '${owner}'.`,
          action: { type: 'owner', object, owner }
        };
      },
      
      help: async () => {
        return {
          message: `I can help you with Unity Catalog operations:

**Creating Objects:**
• "Create a catalog named sales_catalog"
• "Create a schema called sales.customers"  
• "Create a table sales.customers.orders"

**Managing Permissions:**
• "Grant SELECT permission on sales.customers to data_analyst"
• "Revoke MODIFY on sales.orders from john_doe"
• "Show permissions for sales.customers"
• "Set owner of sales.customers to admin_user"

**Listing Objects:**
• "List all catalogs"
• "List schemas in sales_catalog"

Just tell me what you'd like to do in natural language!`,
          action: { type: 'help' }
        };
      },
      
      complex: async () => {
        return {
          message: `This looks like a complex request. Let me break it down into steps. Could you provide more details or rephrase the request?`,
          action: { type: 'clarification' }
        };
      }
    };

    const operation = operations[intent.intent || intent];
    if (operation) {
      return await operation(intent.params || params || []);
    }

    return {
      message: `I'm not sure how to handle that request. Type "help" to see what I can do.`,
      action: { type: 'unknown' }
    };
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Parse intent
      const intent = await parseIntent(input);
      
      // Execute operation
      const result = await executeOperation(intent, []);
      
      // Add to action log
      if (result.sql) {
        setActionLog(prev => [...prev, {
          timestamp: new Date(),
          sql: result.sql,
          action: result.action,
          status: 'success'
        }]);
      }

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: result.message,
        sql: result.sql,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try rephrasing your request.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { label: 'Create Catalog', icon: Database, prompt: 'Create a catalog named ' },
    { label: 'Grant Access', icon: Shield, prompt: 'Grant SELECT permission on ' },
    { label: 'List Catalogs', icon: Terminal, prompt: 'List all catalogs' },
    { label: 'Help', icon: Settings, prompt: 'help' }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b3d 100%)',
      fontFamily: '"Space Mono", "Courier New", monospace',
      color: '#e0e6ed',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <header style={{
        background: 'rgba(15, 20, 40, 0.8)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(100, 255, 218, 0.1)',
        padding: '1.5rem 2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
      }}>
        <Database size={32} style={{ color: '#64ffda' }} />
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '1.5rem',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #64ffda 0%, #8892ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.05em'
          }}>
            Unity Catalog Assistant
          </h1>
          <p style={{
            margin: '0.25rem 0 0 0',
            fontSize: '0.75rem',
            color: '#8892b0',
            letterSpacing: '0.1em'
          }}>
            DATABRICKS GOVERNANCE AI
          </p>
        </div>
      </header>

      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1fr 320px',
        gap: '1px',
        background: 'rgba(100, 255, 218, 0.05)',
        overflow: 'hidden'
      }}>
        {/* Chat Area */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(10, 14, 39, 0.6)',
          backdropFilter: 'blur(8px)'
        }}>
          {/* Messages */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem'
          }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start',
                  animation: 'slideIn 0.3s ease-out',
                  opacity: 0,
                  animationFillMode: 'forwards',
                  animationDelay: `${idx * 0.05}s`
                }}
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: msg.role === 'user' 
                    ? 'linear-gradient(135deg, #8892ff 0%, #a855f7 100%)'
                    : 'linear-gradient(135deg, #64ffda 0%, #00bfa5 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  boxShadow: msg.role === 'user'
                    ? '0 4px 16px rgba(136, 146, 255, 0.3)'
                    : '0 4px 16px rgba(100, 255, 218, 0.3)'
                }}>
                  {msg.role === 'user' ? (
                    <Users size={18} style={{ color: '#fff' }} />
                  ) : (
                    <Database size={18} style={{ color: '#fff' }} />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    background: msg.isError 
                      ? 'rgba(239, 68, 68, 0.1)'
                      : msg.role === 'user'
                        ? 'rgba(136, 146, 255, 0.1)'
                        : 'rgba(100, 255, 218, 0.05)',
                    border: `1px solid ${msg.isError ? 'rgba(239, 68, 68, 0.3)' : 'rgba(100, 255, 218, 0.2)'}`,
                    borderRadius: '12px',
                    padding: '1rem 1.25rem',
                    fontSize: '0.9rem',
                    lineHeight: '1.6',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {msg.content}
                  </div>
                  {msg.sql && (
                    <div style={{
                      marginTop: '0.75rem',
                      background: 'rgba(15, 20, 40, 0.8)',
                      border: '1px solid rgba(100, 255, 218, 0.3)',
                      borderRadius: '8px',
                      padding: '1rem',
                      fontFamily: '"Fira Code", "Courier New", monospace',
                      fontSize: '0.85rem',
                      color: '#64ffda',
                      overflowX: 'auto'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '0.5rem',
                        fontSize: '0.7rem',
                        color: '#8892b0',
                        letterSpacing: '0.1em'
                      }}>
                        <Terminal size={12} />
                        SQL COMMAND
                      </div>
                      <code>{msg.sql}</code>
                    </div>
                  )}
                  <div style={{
                    marginTop: '0.5rem',
                    fontSize: '0.7rem',
                    color: '#8892b0',
                    letterSpacing: '0.05em'
                  }}>
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{
                display: 'flex',
                gap: '1rem',
                alignItems: 'center'
              }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #64ffda 0%, #00bfa5 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Loader size={18} style={{ color: '#fff', animation: 'spin 1s linear infinite' }} />
                </div>
                <div style={{
                  background: 'rgba(100, 255, 218, 0.05)',
                  border: '1px solid rgba(100, 255, 218, 0.2)',
                  borderRadius: '12px',
                  padding: '1rem 1.25rem',
                  fontSize: '0.9rem',
                  color: '#8892b0'
                }}>
                  Processing your request...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div style={{
            padding: '1rem 2rem',
            borderTop: '1px solid rgba(100, 255, 218, 0.1)',
            display: 'flex',
            gap: '0.75rem',
            flexWrap: 'wrap'
          }}>
            {quickActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => setInput(action.prompt)}
                style={{
                  background: 'rgba(100, 255, 218, 0.08)',
                  border: '1px solid rgba(100, 255, 218, 0.3)',
                  borderRadius: '8px',
                  padding: '0.5rem 1rem',
                  color: '#64ffda',
                  fontSize: '0.75rem',
                  fontFamily: 'inherit',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease',
                  letterSpacing: '0.05em'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(100, 255, 218, 0.15)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(100, 255, 218, 0.08)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <action.icon size={14} />
                {action.label}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div style={{
            padding: '1.5rem 2rem',
            background: 'rgba(15, 20, 40, 0.6)',
            borderTop: '1px solid rgba(100, 255, 218, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              gap: '1rem',
              alignItems: 'flex-end'
            }}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe what you'd like to do with Unity Catalog..."
                disabled={isLoading}
                style={{
                  flex: 1,
                  background: 'rgba(10, 14, 39, 0.8)',
                  border: '1px solid rgba(100, 255, 218, 0.3)',
                  borderRadius: '12px',
                  padding: '1rem 1.25rem',
                  color: '#e0e6ed',
                  fontSize: '0.9rem',
                  fontFamily: 'inherit',
                  resize: 'none',
                  minHeight: '56px',
                  maxHeight: '120px',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#64ffda';
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(100, 255, 218, 0.1)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(100, 255, 218, 0.3)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                style={{
                  background: input.trim() && !isLoading
                    ? 'linear-gradient(135deg, #64ffda 0%, #00bfa5 100%)'
                    : 'rgba(100, 255, 218, 0.1)',
                  border: 'none',
                  borderRadius: '12px',
                  width: '56px',
                  height: '56px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease',
                  boxShadow: input.trim() && !isLoading ? '0 4px 16px rgba(100, 255, 218, 0.3)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (input.trim() && !isLoading) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(100, 255, 218, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = input.trim() && !isLoading ? '0 4px 16px rgba(100, 255, 218, 0.3)' : 'none';
                }}
              >
                <Send size={20} style={{ color: input.trim() && !isLoading ? '#0a0e27' : '#8892b0' }} />
              </button>
            </div>
          </div>
        </div>

        {/* Action Log Sidebar */}
        <div style={{
          background: 'rgba(15, 20, 40, 0.8)',
          backdropFilter: 'blur(8px)',
          borderLeft: '1px solid rgba(100, 255, 218, 0.1)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid rgba(100, 255, 218, 0.1)'
          }}>
            <h2 style={{
              margin: 0,
              fontSize: '1rem',
              fontWeight: 600,
              color: '#64ffda',
              letterSpacing: '0.1em',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Terminal size={16} />
              ACTION LOG
            </h2>
          </div>
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '1rem'
          }}>
            {actionLog.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '2rem 1rem',
                color: '#8892b0',
                fontSize: '0.85rem'
              }}>
                No actions yet. Start a conversation to see executed commands here.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {actionLog.slice().reverse().map((log, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(10, 14, 39, 0.6)',
                      border: '1px solid rgba(100, 255, 218, 0.2)',
                      borderRadius: '8px',
                      padding: '0.75rem',
                      fontSize: '0.75rem',
                      animation: 'slideIn 0.3s ease-out'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.5rem',
                      color: log.status === 'success' ? '#64ffda' : '#ef4444'
                    }}>
                      {log.status === 'success' ? (
                        <CheckCircle size={12} />
                      ) : (
                        <AlertCircle size={12} />
                      )}
                      <span style={{ letterSpacing: '0.05em' }}>
                        {log.action.type.toUpperCase()}
                      </span>
                    </div>
                    <div style={{
                      color: '#8892b0',
                      fontSize: '0.7rem',
                      marginBottom: '0.5rem',
                      wordBreak: 'break-word'
                    }}>
                      {log.sql}
                    </div>
                    <div style={{
                      color: '#64748b',
                      fontSize: '0.65rem',
                      letterSpacing: '0.05em'
                    }}>
                      {log.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        * {
          box-sizing: border-box;
        }
        
        textarea::placeholder {
          color: #8892b0;
        }
        
        ::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(15, 20, 40, 0.4);
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(100, 255, 218, 0.3);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(100, 255, 218, 0.5);
        }
      `}</style>
    </div>
  );
};

export default UnityCatalogChatbot;
