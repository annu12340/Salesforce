import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'primary',
  size = 'md',
  className = '',
  ...props 
}) => {
  const baseClasses = "flex items-center justify-center rounded-full font-medium transition-all";
  
  const variantClasses = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white",
    secondary: "bg-purple-600 hover:bg-purple-700 text-white",
    danger: "bg-red-500 hover:bg-red-600 text-white",
    subtle: "bg-white/70 hover:bg-white/90 text-gray-900 border border-white/30",
  };
  
  const sizeClasses = {
    sm: "text-sm px-4 py-2",
    md: "text-base px-6 py-3",
    lg: "text-lg px-8 py-4",
    icon: "w-12 h-12",
    'icon-lg': "w-20 h-20",
  };
  
  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "";
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${className}`;
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={classes}
      {...props}
    >
      {children}
    </button>
  );
}; 