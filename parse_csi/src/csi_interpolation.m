function interp_csi = csi_interpolation(name, csi_trace, interp_interval, sec, power, start_idx, sz) 
	%size(csi_trace)
	if ~exist('power', 'var')
		power = 1;
	end
	if ~exist('start_idx', 'var')
		start_idx = 100;
	end
	if ~exist('sz', 'var')
		sz = 120;
	end

	phase_mat = [];

	csi_mat = [];
	ori_timestamp = [];
	for idx = start_idx:size(csi_trace, 1)
		csi = csi_trace{idx}.csi;

		phase_mat = [phase_mat, reshape(csi(1,2,:), [30,1])];
		if csi_trace{idx}.perm(end) ~= 3
			input('here')
		end

		% Find the permutation of Rx ants
		ant_1st = find(csi_trace{idx}.perm == 1);
		ant_2nd = find(csi_trace{idx}.perm == 2);
	
		shape = size(csi, 1)*size(csi, 2)*size(csi,3);
		if shape ~= 180 && shape ~= 120
			continue 
		end 

		ori_timestamp = [ori_timestamp, csi_trace{idx}.timestamp_low];

		% Transform into a column vector with subcarriers of the same ant pair together (30*n)*1
		%csi = reshape(csi(:,[ant_1st, ant_2nd],:), 4, sz/4);
		csi = reshape(csi(:,1:2,:), 4, sz/4);
		csi = reshape(csi', sz, 1);
		csi_mat = [csi_mat, csi];
	end

	if size(csi_mat,2) == 0
		interp_csi = 0;
		return
	end
	ori_timestamp = ori_timestamp - ori_timestamp(1);

	%{
	cf = 1;
	fig = figure(cf); clf;
	a = repmat(0, 1, 5000);
	ms = int32(ori_timestamp/1000+1);
	for idx = 1:size(ms, 2)
		a(1, ms(1, idx)) = 256;
	end
	image(a);
	colormap('gray');

	str = strcat('timestamp/', name, '.jpg');
	saveas(fig, str{1});
	clf;

	interp_csi = csi_mat;
	return;

	offset = 1; sub = 1;
	para = 10000; %size(phase_mat, 2);
	if size(csi_trace, 1) >= offset+para-1
		plot(ori_timestamp(1, offset:offset+para-1),angle(phase_mat(sub, offset:offset+para-1)));
		%scatter(offset:offset+para-1,angle(phase_mat(sub, offset:offset+para-1)));

		str = strcat('phase/', name, '.jpg');
		saveas(fig, str{1});
		hold off;
	end
	%input('done plotting')
	%}

	% Check the number of duplicate timestamp
	% and remove all duplicated samples
	curr_timestamp = ori_timestamp(1, 1);
	idx = [];
	cnt = 0;
	for i = 2:size(ori_timestamp, 2)
		if ori_timestamp(1,i) == curr_timestamp
			idx = [idx, i];
			cnt = cnt + 1;
		end
		curr_timestamp = ori_timestamp(1,i);
	end
	disp 'duplicated number:'  
	disp (cnt)

	csi_mat(:,idx) 		 = [];
	ori_timestamp(:,idx) = [];

	% Do interpolation to interp_interval CSI/s
	interp_csi = [];
	new_timestamp = interp_interval:interp_interval:min(sec * 10^6, ori_timestamp(end));
	for row = 1:size(csi_mat, 1) 
		if power == 1
			ori_mat = abs(csi_mat(row,:)).^2;
		else
			ori_mat = abs(csi_mat(row,:));
		end

		% Interpolate to the end of timestamp
		%interp_csi = [interp_csi; interp1(ori_timestamp, ori_mat, new_timestamp)];
		interp_csi = [interp_csi; ori_mat];
	end
end
