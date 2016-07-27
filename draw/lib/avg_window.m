function signal_new = avg_window(sz, signal)
	sub_cnt = size(signal, 1);
	signal_new = zeros(size(signal));

	for idx = 1:sub_cnt
	    sub_avg = 0;
	    for i = 1:size(signal, 2) - 1 
	        if i - sz < 1
	            sub_avg = (sub_avg * (i - 1) + signal(idx, i)) / i;
	        else
	            sub_avg = sub_avg + (signal(idx, i) - signal(idx, i - sz)) / sz;
	        end
					%if i > 300
					%	i
					%	signal(idx, i + 1)
					%	abs(signal(idx, i + 1))
					%	disp('----------')
					%	sub_avg
					%	abs(sub_avg)
					%	input('hello', 's');
					%end
	        signal_new(idx, i + 1) = signal(idx, i + 1) - sub_avg;
	    end
	end
end
