import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { StickyNote, Type, Image as ImageIcon, Video, MoreVertical, Edit2, Copy, Trash2, Sparkles, FileText, RefreshCw } from 'lucide-react';
import clsx from 'clsx';

const NodeHeader = ({ type, label, onDelete, onDuplicate, onEdit, onRegenerate }: { type: string, label: string, onDelete: () => void, onDuplicate: () => void, onEdit: () => void, onRegenerate?: () => void }) => {
  const [menuOpen, setMenuOpen] = React.useState(false);

  let Icon = StickyNote;
  if (type === 'text') Icon = Type;
  else if (type === 'video') Icon = Video;
  else if (type === 'image') Icon = ImageIcon;
  else if (type === 'ai-note') Icon = Sparkles;
  else if (type === 'summary') Icon = FileText;

  return (
    <div className="flex items-center justify-between mb-2 border-b border-black/5 pb-2">
      <div className={clsx("flex items-center text-xs font-bold uppercase", type === 'ai-note' || type === 'summary' ? "text-indigo-600" : "text-gray-500")}>
        <Icon size={14} className="mr-1.5" />
        {label}
      </div>
      <div className="relative flex items-center gap-1">
        {(type === 'ai-note' || type === 'summary' || type === 'video' || type === 'image' || type === 'text') && onRegenerate && (
          <button 
            onClick={(e) => {
              e.stopPropagation();
              onRegenerate();
            }}
            className="text-indigo-400 hover:text-indigo-600 p-1 rounded-full hover:bg-indigo-50"
            title="Regenerate"
          >
            <RefreshCw size={14} />
          </button>
        )}
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpen(!menuOpen);
          }}
          className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-black/5"
        >
          <MoreVertical size={16} />
        </button>
        
        {menuOpen && (
          <div className="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-100 z-50 overflow-hidden">
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
                setMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
            >
              <Edit2 size={14} className="mr-2" /> Edit
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onDuplicate();
                setMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
            >
              <Copy size={14} className="mr-2" /> Duplicate
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
                setMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
            >
              <Trash2 size={14} className="mr-2" /> Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export const CustomNode = memo(({ data, id }: NodeProps) => {
  const [expanded, setExpanded] = React.useState(false);
  const content = data.content || '';
  const isLongContent = content.length > 180;
  const displayContent = (isLongContent && !expanded) ? content.slice(0, 180) + '...' : content;

  return (
    <div className={clsx("px-4 py-3 rounded-lg shadow-sm border w-72 transition-all hover:shadow-md bg-white", data.color || 'border-gray-200', expanded && "z-50")}>
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-indigo-500" />
      
      <NodeHeader 
        type={data.type} 
        label={data.type === 'ai-note' ? 'AI Note' : data.type === 'summary' ? 'Summary' : data.type} 
        onDelete={() => data.onDelete(id)}
        onDuplicate={() => data.onDuplicate(data)}
        onEdit={() => data.onEdit(id)}
        onRegenerate={data.onRegenerate ? () => data.onRegenerate(id) : undefined}
      />
      
      <div className="text-sm text-gray-800 font-medium whitespace-pre-wrap leading-relaxed">
        {data.isLoading ? (
          <div className="flex items-center text-gray-400 italic py-2">
            <RefreshCw size={14} className="animate-spin mr-2" /> Generating...
          </div>
        ) : (
          <div>
            {displayContent || <span className="text-gray-400 italic">Empty content...</span>}
            {isLongContent && (
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setExpanded(!expanded);
                }}
                className="mt-2 text-indigo-600 hover:text-indigo-700 text-xs font-bold flex items-center bg-indigo-50/50 px-2 py-1 rounded w-fit"
              >
                {expanded ? 'Show Less' : 'Show More'}
              </button>
            )}
          </div>
        )}
      </div>
      
      {data.context && (
        <div className="mt-2 pt-2 border-t border-black/5">
          <p className="text-xs text-gray-500 italic">{data.context}</p>
        </div>
      )}

      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-indigo-500" />
    </div>
  );
});
