function parse_csi(folder, action_dir, power, sz, interp_interval, sec)
	addpath('/tmp4/transfer/WiSee/linux-80211n-csitool-supplementary/matlab');
	start_idx = 100;
	num_sub = 30;

	% sz: #antenna pair * #subcarrier (30)
	if ~exist('sz', 'var')
		sz = 120;
	end
	% Interval: micro-second
	if ~exist('interp_interval', 'var')
		interp_interval = 1000;
	end
	% sec: recorded seconds
	if ~exist('sec', 'var')
		sec = 5;
	end

	folder
	files = dir([folder '/*.bin']);
	for file = files'
		names = strsplit(file.name, '.');
		name = names(1)

		csi_mat = [];
		ori_timestamp = [];
		csi_trace = read_bf_file([folder '/' file.name]);
	
		for idx = start_idx:size(csi_trace, 1)
			csi = csi_trace{idx};
			csi = csi.csi;
			%csi = get_scaled_csi(csi);

			ant_1st = find(csi_trace{idx}.perm == 1);
			ant_2nd = find(csi_trace{idx}.perm == 2);
			ant_3rd = find(csi_trace{idx}.perm == 3);

	
			% When there are 2*3 Tx-Rx ants pairs
			% Pick 1*3 pairs where abs of two Tx ants are closer
			shape = size(csi, 1)*size(csi, 2)*size(csi,3);

			ori_timestamp = [ori_timestamp, csi_trace{idx}.timestamp_low];

			% Transform into a column vector with subcarriers of the same ant pair together (30*n)*1
			%csi(:, [ant_1st, ant_2nd], :);
			csi = reshape(csi(:, 1:2, :), 4, sz / 4);
			%csi = reshape(csi(:, [ant_1st, ant_2nd], :), 4, sz / 4);
			csi = reshape(csi', sz, 1);
			csi_mat = [csi_mat, csi];
		end
		size(csi_mat)
		ori_timestamp = ori_timestamp - ori_timestamp(1);

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
		%csi_mat(:,idx) = [];
		%ori_timestamp(:,idx) = [];

		% Do interpolation to 1000 CSI/s
		if ~exist(action_dir, 'dir')
			mkdir(action_dir)
		end

		new_timestamp = interp_interval:interp_interval:min(sec * 10^6, ori_timestamp(end));

		ori_mat = [];
		for row = 1:size(csi_mat, 1) 
			if power == 1
				tmp_row = abs(csi_mat(row,:)).^2;
			elseif power == 0
				tmp_row = abs(csi_mat(row,:));
			else
				tmp_row = csi_mat(row,:);
			end

			% Interpolate to the end of timestamp
			%tmp_row = interp1(ori_timestamp,tmp_row,new_timestamp);
			ori_mat = [ori_mat; tmp_row];
		end
		size(ori_mat)

		save(cell2mat([action_dir '/' name '.mat']), 'ori_mat');
	end
end
