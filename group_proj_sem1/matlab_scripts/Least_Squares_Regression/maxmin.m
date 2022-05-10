function [max, min] = maxmin(xdata, col)
if isempty(xdata)
  error('Input xdata is empty'); 
end
value = sort(xdata(:,col));
min    = value(1);
max    = value(end);
