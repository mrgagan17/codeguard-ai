import React from 'react';
import { Category } from '../types';
import { ShieldAlert, Sparkles, Code2, AlertTriangle, Key, Bug } from 'lucide-react';

interface CategoryBadgeProps {
  category: Category;
  className?: string;
}

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category, className = '' }) => {
  const getIcon = () => {
    switch (category) {
      case 'security':
        return <ShieldAlert className="w-3.5 h-3.5 mr-1 text-red-400" />;
      case 'secret':
        return <Key className="w-3.5 h-3.5 mr-1 text-amber-400" />;
      case 'bug_risk':
        return <Bug className="w-3.5 h-3.5 mr-1 text-orange-400" />;
      case 'complexity':
        return <AlertTriangle className="w-3.5 h-3.5 mr-1 text-yellow-400" />;
      case 'quality':
        return <Sparkles className="w-3.5 h-3.5 mr-1 text-blue-400" />;
      case 'style':
      default:
        return <Code2 className="w-3.5 h-3.5 mr-1 text-slate-400" />;
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[#141414] text-[#CCCCCC] border border-[#262626] ${className}`}
    >
      {getIcon()}
      <span className="capitalize">{category.replace('_', ' ')}</span>
    </span>
  );
};
