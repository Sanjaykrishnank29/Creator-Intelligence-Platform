import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  useNodesState, 
  useEdgesState, 
  addEdge, 
  Connection, 
  Edge, 
  Node,
  ReactFlowProvider,
  Panel,
  useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Plus, StickyNote, Image as ImageIcon, Video, Type, MessageSquare, Send, X, Sparkles, LayoutGrid, FileText, Undo2, Redo2, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import clsx from 'clsx';
import { CustomNode } from '../components/CustomNodes';
import CustomEdge from '../components/CustomEdge';
import { apiUrl } from '../api';
import ReactMarkdown from 'react-markdown';

const nodeTypes = {
  custom: CustomNode,
};

const edgeTypes = {
  custom: CustomEdge,
};

interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

const initialNodes: Node[] = [
  { 
    id: '1', 
    type: 'custom', 
    position: { x: 100, y: 100 }, 
    data: { type: 'note', content: 'Info / News / Ideas', context: 'Raw inputs', color: 'bg-yellow-50 border-yellow-200' } 
  },
  { 
    id: '2', 
    type: 'custom', 
    position: { x: 400, y: 100 }, 
    data: { type: 'summary', content: 'Collection Summary', context: 'Synthesized insights', color: 'bg-blue-50 border-blue-200' } 
  },
  { 
    id: '3', 
    type: 'custom', 
    position: { x: 700, y: 100 }, 
    data: { type: 'text', content: 'General Script', context: 'Core narrative', color: 'bg-green-50 border-green-200' } 
  },
  { 
    id: '4', 
    type: 'custom', 
    position: { x: 1000, y: 0 }, 
    data: { type: 'video', content: 'YouTube Script', context: 'Long-form video', color: 'bg-red-50 border-red-200' } 
  },
  { 
    id: '5', 
    type: 'custom', 
    position: { x: 1000, y: 150 }, 
    data: { type: 'image', content: 'Instagram Post', context: 'Visual + Caption', color: 'bg-pink-50 border-pink-200' } 
  },
  { 
    id: '6', 
    type: 'custom', 
    position: { x: 1000, y: 300 }, 
    data: { type: 'text', content: 'Twitter Thread', context: 'Short-form text', color: 'bg-sky-50 border-sky-200' } 
  },
  { 
    id: '7', 
    type: 'custom', 
    position: { x: 1300, y: 150 }, 
    data: { type: 'ai-note', content: 'Enhanced Prompts & Ideas', context: 'Thumbnails, Hooks, Engagement', color: 'bg-purple-50 border-purple-200' } 
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, type: 'custom' },
  { id: 'e2-3', source: '2', target: '3', animated: true, type: 'custom' },
  { id: 'e3-4', source: '3', target: '4', animated: true, type: 'custom' },
  { id: 'e3-5', source: '3', target: '5', animated: true, type: 'custom' },
  { id: 'e3-6', source: '3', target: '6', animated: true, type: 'custom' },
  { id: 'e4-7', source: '4', target: '7', animated: true, type: 'custom' },
  { id: 'e5-7', source: '5', target: '7', animated: true, type: 'custom' },
  { id: 'e6-7', source: '6', target: '7', animated: true, type: 'custom' },
];

export default function CreatorEngine() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([{ role: 'model', text: 'Hi! I\'m your Creator Assistant. I can help you generate ideas, summarize doubts, or alternate content. How can I help?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatWidth, setChatWidth] = useState(380);
  const isResizing = useRef(false);
  const [editingNode, setEditingNode] = useState<Node | null>(null);
  const [contextMenu, setContextMenu] = useState<{ x: number, y: number } | null>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  // Undo/Redo History
  const [history, setHistory] = useState<{ nodes: Node[], edges: Edge[] }[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Save state to history
  const takeSnapshot = useCallback(() => {
    setHistory(prev => {
      const newHistory = prev.slice(0, historyIndex + 1);
      newHistory.push({ nodes, edges });
      return newHistory;
    });
    setHistoryIndex(prev => prev + 1);
  }, [nodes, edges, historyIndex]);

  // Initial snapshot
  useEffect(() => {
    if (history.length === 0) {
      setHistory([{ nodes, edges }]);
      setHistoryIndex(0);
    }
  }, []);

  // Window resize listeners
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;
      e.preventDefault();
      // Calculate new width: viewport width - mouse X position
      // Ensure min 300px and max 800px width
      const newWidth = Math.min(Math.max(window.innerWidth - e.clientX, 300), 800);
      setChatWidth(newWidth);
    };

    const handleMouseUp = () => {
      if (isResizing.current) {
        isResizing.current = false;
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto'; // Re-enable text selection
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const prevState = history[historyIndex - 1];
      setNodes(prevState.nodes);
      setEdges(prevState.edges);
      setHistoryIndex(prev => prev - 1);
    }
  }, [history, historyIndex, setNodes, setEdges]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1];
      setNodes(nextState.nodes);
      setEdges(nextState.edges);
      setHistoryIndex(prev => prev + 1);
    }
  }, [history, historyIndex, setNodes, setEdges]);

  // Keyboard shortcuts for Undo/Redo
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        undo();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'y') {
        e.preventDefault();
        redo();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo]);

  const onConnect = useCallback((params: Connection) => {
    takeSnapshot();
    setEdges((eds) => addEdge({ ...params, animated: true, type: 'custom' }, eds));
    
    // Auto-summarize if connecting to a summary node
    const targetNode = nodes.find(n => n.id === params.target);
    if (targetNode && targetNode.data.type === 'summary') {
      handleRegenerate(targetNode.id);
    }
  }, [setEdges, takeSnapshot, nodes]);

  const handleDeleteNode = useCallback((id: string) => {
    takeSnapshot();
    setNodes((nds) => nds.filter((node) => node.id !== id));
  }, [setNodes, takeSnapshot]);

  const handleDuplicateNode = useCallback((nodeData: any) => {
    takeSnapshot();
    const newNode = {
      id: Date.now().toString(),
      type: 'custom',
      position: { x: Math.random() * 100 + 100, y: Math.random() * 100 + 100 },
      data: { ...nodeData, id: Date.now().toString() },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [setNodes, takeSnapshot]);

  const handleRegenerate = useCallback(async (id: string) => {
    const node = nodes.find(n => n.id === id);
    if (!node) return;

    // Set loading state
    setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, isLoading: true } } : n));

    try {
      if (node.data.type === 'summary' || node.data.type === 'video' || node.data.type === 'image' || node.data.type === 'text') {
        // Find connected source nodes
        const sourceEdges = edges.filter(e => e.target === id);
        const sourceNodes = nodes.filter(n => sourceEdges.some(e => e.source === n.id));
        const contents = sourceNodes.map(n => n.data.content).filter(Boolean);

        if (contents.length === 0 && node.data.type === 'summary') {
          setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, isLoading: false, content: 'Connect nodes to summarize...' } } : n));
          return;
        }

        const payload: any = { contents };
        if (node.data.type !== 'summary') {
          payload.platform = node.data.content.toLowerCase().includes('youtube') ? 'YouTube' : 
                            node.data.content.toLowerCase().includes('instagram') ? 'Instagram' : 
                            node.data.content.toLowerCase().includes('twitter') ? 'Twitter' : 'General';
          payload.target_type = node.data.type;
          
          // If no parents for a script, try to use its own content as "base"
          if (contents.length === 0) {
            payload.contents = [node.data.content];
          }
        }

        const res = await fetch(apiUrl('/api/summarize'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const raw = await res.json();
        // Unwrap API Gateway envelope
        const data = (raw.statusCode && raw.body) ? JSON.parse(raw.body) : raw;
        
        setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, isLoading: false, content: data.summary || data.response || 'Failed to generate' } } : n));
      } else if (node.data.type === 'ai-note') {
        const rawNiche = node.data.context?.trim() || node.data.content?.trim() || '';
        const isPlaceholder = rawNiche.includes('Click regenerate') || rawNiche.includes('New ai-note') || rawNiche === 'Enhanced Prompts & Ideas';
        const niche = isPlaceholder ? '' : rawNiche;
        
        const res = await fetch(apiUrl('/api/generate'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ niche, platform: 'YouTube', creator_id: 'techwithtim', bust_cache: true })
        });
        const raw = await res.json();
        // Unwrap API Gateway envelope + extract first idea or ideas text
        const data = (raw.statusCode && raw.body) ? JSON.parse(raw.body) : raw;
        const content = (data.ideas && data.ideas.length > 0) ? `${data.ideas[0].title}: ${data.ideas[0].explanation}` : (data.content || 'Failed to generate');
        
        setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, isLoading: false, content } } : n));
      }
    } catch (error) {
      console.error(error);
      setNodes(nds => nds.map(n => n.id === id ? { ...n, data: { ...n.data, isLoading: false, content: 'Error — check console' } } : n));
    }
  }, [nodes, edges, setNodes]);

  const handleEditNode = useCallback((nodeId: string) => {
    setEditingNode(nodes.find(n => n.id === nodeId) || null);
  }, [nodes]);

  // Update nodes with handlers
  const nodesWithHandlers = nodes.map(node => ({
    ...node,
    data: {
      ...node.data,
      onDelete: handleDeleteNode,
      onDuplicate: handleDuplicateNode,
      onEdit: (id: string) => handleEditNode(id),
      onRegenerate: handleRegenerate
    }
  }));

  const addNode = (type: string, position?: { x: number, y: number }) => {
    takeSnapshot();
    const newNode: Node = {
      id: Date.now().toString(),
      type: 'custom',
      position: position || { x: Math.random() * 400, y: Math.random() * 400 },
      data: { 
        type, 
        content: type === 'summary' ? 'Connect nodes to summarize...' : type === 'ai-note' ? 'Click regenerate to create content...' : `New ${type}`, 
        context: '', 
        color: type === 'note' ? 'bg-yellow-50 border-yellow-200' : 
               type === 'summary' ? 'bg-indigo-50 border-indigo-200' :
               type === 'ai-note' ? 'bg-purple-50 border-purple-200' :
               'bg-white border-gray-200' 
      },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const onPaneContextMenu = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      setContextMenu({ x: event.clientX, y: event.clientY });
    },
    []
  );

  const onPaneClick = useCallback(() => setContextMenu(null), []);

  const handleContextMenuAdd = (type: string) => {
    if (reactFlowInstance && contextMenu) {
      const position = reactFlowInstance.screenToFlowPosition({
        x: contextMenu.x,
        y: contextMenu.y,
      });
      addNode(type, position);
      setContextMenu(null);
    }
  };

  const handleEditSave = () => {
    if (editingNode) {
      takeSnapshot();
      setNodes((nds) => nds.map((node) => {
        if (node.id === editingNode.id) {
          return {
            ...node,
            data: {
              ...node.data,
              content: editingNode.data.content,
              context: editingNode.data.context,
            }
          };
        }
        return node;
      }));
      setEditingNode(null);
    }
  };

  const handleChatSubmit = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(apiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history: messages })
      });
      const raw = await res.json();
      // Unwrap API Gateway envelope
      const data = (raw.statusCode && raw.body) ? JSON.parse(raw.body) : raw;
      if (data.response) {
        setMessages(prev => [...prev, { role: 'model', text: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'model', text: 'Sorry, I encountered an error. ' + (data.error || '') }]);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'model', text: 'Sorry, connection failed.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full w-full relative overflow-hidden">
      {/* Floating Chatbot Button (Bottom Right) */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="absolute bottom-6 right-6 z-50 flex items-center justify-center w-14 h-14 bg-indigo-600 text-white rounded-full shadow-lg hover:bg-indigo-700 hover:scale-105 transition-transform"
          title="Open Creator Assistant"
        >
          <Bot size={28} />
        </button>
      )}

      <div className="flex-1 bg-gray-50 relative overflow-hidden rounded-xl border border-gray-200 shadow-inner h-full" ref={reactFlowWrapper}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodesWithHandlers}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            onPaneContextMenu={onPaneContextMenu}
            onPaneClick={onPaneClick}
            onInit={setReactFlowInstance}
            fitView
            attributionPosition="bottom-right"
            className="bg-gray-50"
          >
            <Background color="#cbd5e1" gap={20} size={1} />
            <Controls />
            <MiniMap />
            
            <Panel position="top-left" className="flex gap-2">
              <div className="bg-white p-2 rounded-lg shadow-md border border-gray-100 flex flex-col gap-2">
                <button onClick={() => addNode('note')} className="p-2 hover:bg-gray-100 rounded-md text-gray-600" title="Add Note">
                  <StickyNote size={20} />
                </button>
                <button onClick={() => addNode('text')} className="p-2 hover:bg-gray-100 rounded-md text-gray-600" title="Add Text">
                  <Type size={20} />
                </button>
                <button onClick={() => addNode('image')} className="p-2 hover:bg-gray-100 rounded-md text-gray-600" title="Add Image">
                  <ImageIcon size={20} />
                </button>
                <button onClick={() => addNode('video')} className="p-2 hover:bg-gray-100 rounded-md text-gray-600" title="Add Video">
                  <Video size={20} />
                </button>
                <div className="h-px bg-gray-200 my-1" />
                <button onClick={() => addNode('ai-note')} className="p-2 hover:bg-gray-100 rounded-md text-purple-600" title="Add AI Note">
                  <Sparkles size={20} />
                </button>
                <button onClick={() => addNode('summary')} className="p-2 hover:bg-gray-100 rounded-md text-indigo-600" title="Add Summary">
                  <FileText size={20} />
                </button>
              </div>
            </Panel>

            <Panel position="top-right" className="flex gap-2">
              <button 
                onClick={undo} 
                disabled={historyIndex <= 0}
                className="bg-white p-2 rounded-lg shadow-md border border-gray-100 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Undo (Ctrl+Z)"
              >
                <Undo2 size={20} />
              </button>
              <button 
                onClick={redo} 
                disabled={historyIndex >= history.length - 1}
                className="bg-white p-2 rounded-lg shadow-md border border-gray-100 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                title="Redo (Ctrl+Y)"
              >
                <Redo2 size={20} />
              </button>
            </Panel>
          </ReactFlow>
        </ReactFlowProvider>
        
        {/* Context Menu */}
        {contextMenu && (
          <div 
            className="fixed bg-white rounded-lg shadow-xl border border-gray-100 z-50 py-1 w-48"
            style={{ top: contextMenu.y, left: contextMenu.x }}
          >
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-100 mb-1">
              Add Node
            </div>
            <button onClick={() => handleContextMenuAdd('note')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <StickyNote size={16} className="mr-2 text-yellow-500" /> Note
            </button>
            <button onClick={() => handleContextMenuAdd('text')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <Type size={16} className="mr-2 text-blue-500" /> Text
            </button>
            <button onClick={() => handleContextMenuAdd('image')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <ImageIcon size={16} className="mr-2 text-pink-500" /> Image
            </button>
            <button onClick={() => handleContextMenuAdd('video')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <Video size={16} className="mr-2 text-red-500" /> Video
            </button>
            <div className="border-t border-gray-100 my-1" />
            <button onClick={() => handleContextMenuAdd('ai-note')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <Sparkles size={16} className="mr-2 text-purple-500" /> AI Note
            </button>
            <button onClick={() => handleContextMenuAdd('summary')} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
              <FileText size={16} className="mr-2 text-indigo-500" /> Summary
            </button>
          </div>
        )}

        {/* Edit Modal */}
        {editingNode && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Edit Node</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                  <textarea
                    value={editingNode.data.content}
                    onChange={(e) => setEditingNode({
                      ...editingNode,
                      data: { ...editingNode.data, content: e.target.value }
                    })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {editingNode.data.type === 'ai-note' ? 'Prompt (Context)' : 'Context'}
                  </label>
                  <input
                    type="text"
                    value={editingNode.data.context || ''}
                    onChange={(e) => setEditingNode({
                      ...editingNode,
                      data: { ...editingNode.data, context: e.target.value }
                    })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder={editingNode.data.type === 'ai-note' ? "Enter prompt for AI..." : "Add context..."}
                  />
                </div>
                <div className="flex justify-end gap-3 pt-2">
                  <button 
                    onClick={() => setEditingNode(null)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleEditSave}
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chat Bot Panel (Moved to Right Side) */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0, x: 20 }}
            animate={{ width: chatWidth, opacity: 1, x: 0 }}
            exit={{ width: 0, opacity: 0, x: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            style={{ width: chatWidth, minWidth: chatOpen ? 300 : 0 }}
            className="bg-gray-50 border-l border-gray-200 flex flex-col overflow-hidden z-20 h-full relative"
          >
            {/* Draggable Handle */}
            <div 
              className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-indigo-400 hover:w-1.5 transition-all z-50 delay-75 group"
              onMouseDown={(e) => {
                e.preventDefault();
                isResizing.current = true;
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none'; // Prevent text selection while dragging
              }}
            />
            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-white shadow-sm z-10">
              <div className="flex items-center text-indigo-700 font-bold tracking-tight">
                <Sparkles size={20} className="mr-2.5 text-indigo-500" />
                Creator Assistant
              </div>
              <button 
                onClick={() => setChatOpen(false)} 
                className="text-gray-400 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 p-1.5 rounded-md transition-colors"
                title="Close Assistant"
              >
                <X size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-white">
              {messages.map((msg, idx) => (
                <div key={idx} className={clsx("flex flex-col max-w-[90%]", msg.role === 'user' ? "ml-auto items-end" : "items-start")}>
                  <div className={clsx(
                    "p-3.5 rounded-2xl text-sm leading-relaxed", 
                    msg.role === 'user' 
                      ? "bg-indigo-600 text-white rounded-br-sm shadow-md" 
                      : "bg-gray-50 border border-gray-100 shadow-sm text-gray-800 rounded-bl-sm"
                  )}>
                    {msg.role === 'model' ? (
                      <div className="prose prose-sm prose-indigo max-w-none prose-p:leading-relaxed prose-pre:bg-gray-800 prose-pre:text-gray-100">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    ) : (
                      <span className="whitespace-pre-wrap">{msg.text}</span>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex items-center text-indigo-400 text-sm font-medium p-2 animate-pulse">
                  <Sparkles size={16} className="animate-spin mr-2.5" /> Analyzing request...
                </div>
              )}
            </div>
            <div className="p-4 bg-white border-t border-gray-100 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
              <div className="flex gap-2 relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChatSubmit()}
                  placeholder="Ask for ideas, summaries..."
                  className="flex-1 border border-gray-200 bg-gray-50 rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-inner"
                />
                <button 
                  onClick={handleChatSubmit}
                  disabled={loading || !input.trim()}
                  className="absolute right-1.5 top-1.5 bottom-1.5 bg-indigo-600 text-white w-9 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 flex items-center justify-center transition-colors shadow-sm"
                >
                  <Send size={16} className="ml-0.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
