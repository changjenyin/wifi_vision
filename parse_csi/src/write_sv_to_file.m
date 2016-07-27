function write_sv_to_file(svs, names, output_dir)		
	action_dic = containers.Map;
	action_key = {'still', 'jump', 'pickbox', 'run', 'swing', 'walk'};
	action_val = {0, 1, 2, 3, 4, 5};

	for i = 1:length(action_key)
		action_dic(action_key{i}) = action_val{i};
	end
	keys(action_dic);

	if ~exist(output_dir, 'dir')
		mkdir(output_dir);
	end

	fp = fopen([output_dir '/1_feat'], 'w');
	for col = 1:size(svs, 2)
		name = char(names{col});
		%norm_sv = normalizeSV(svs(:, col));
		fprintf(fp, '%s ', name);
		fprintf(fp, '%f ', svs(:, col));

		action = regexprep(name, '\d', '');
		fprintf(fp, '%d', action_dic(action));
		fprintf(fp, '\n');
	end
	fclose(fp);
end

function norm_sv = normalizeSV(sv)
	norm_sv = sv / sum(sv);
end
