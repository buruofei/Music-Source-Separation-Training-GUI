import subprocess
import inquirer
from inquirer.themes import Default
from blessed import Terminal
from colorama import Fore, Style, just_fix_windows_console
import json
import os
from art import text2art
import winsound
import time

'''
v1.2.1
'''

term = Terminal()
just_fix_windows_console()
os.system('title MSST一键包 v1.3     by 领航员未鸟')
inference_base = '.\env\python.exe inference_modified.py'
default_config = {
    "preset_name": ".前次流程",
    "vocal_model_name": "MelBandRoformer_kim.ckpt",
    "kara_model_name": "mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt",
    "reverb_model_name": "dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt",
    "denoise_model_name": False,
    "if_fast": True
}
default_config_path = f".\presets\{default_config['preset_name']}.json"
default_options = {
    "choices": [
        default_config['preset_name']
    ]
}


class CustomTheme(Default):
    def __init__(self):
        super().__init__()
        self.Question.mark_color = term.yellow
        self.Question.brackets_color = term.normal
        self.Question.default_color = term.normal
        self.Editor.opening_prompt_color = term.bright_black
        self.Checkbox.selection_color = term.cyan
        self.Checkbox.selection_icon = ">"
        self.Checkbox.selected_icon = "[X]"
        self.Checkbox.selected_color = term.yellow + term.bold
        self.Checkbox.unselected_color = term.normal
        self.Checkbox.unselected_icon = "[ ]"
        self.Checkbox.locked_option_color = term.gray50
        self.List.selection_color = term.cyan
        self.List.selection_cursor = ">>"
        self.List.unselected_color = term.normal


def play_sound():
    frequencies = [1000, 1500, 1000, 2000]
    duration = 300
    for freq in frequencies:
        winsound.Beep(freq, duration)
        time.sleep(0.1)


def read_config(file_path):
    """读取 JSON 配置文件"""
    with open(file_path, 'r') as file:
        return json.load(file)


def write_config(file_path, config):
    """写入 JSON 配置文件"""
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)


def check_config(file_path):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(Fore.RED + '[INFO]' + Style.RESET_ALL + f' "{file_path}" 文件存在，读取配置...\n')
    else:
        print(Fore.RED + '[INFO]' + Style.RESET_ALL + f' "{file_path}" 文件不存在，创建新配置文件...\n')
        config = default_config
        write_config(file_path, config)


def update_options(presets_folder='presets', options_file='options.json'):
    if not os.path.exists(presets_folder):
        raise ValueError(f"'{presets_folder}' 不存在.")

    preset_files = [f for f in os.listdir(presets_folder) if f.endswith('.json')]
    preset_names = [os.path.splitext(f)[0] for f in preset_files]
    options_data = {'choices': preset_names}
    write_config(options_file, options_data)
    # print(f"{options_file} updated with presets from '{presets_folder}'.")


def save_presets(config, options_file='options.json'):
    preset_name = config.get('preset_name')
    if not preset_name:
        raise ValueError("config 字典中必须包含 'preset_name' 键")
    config_filename = f"{preset_name}.json"
    write_config(f'./presets/{config_filename}', config)
    update_options('presets', options_file)


def determine_module_inputs(vocal_model_name, kara_model_name, reverb_model_name, denoise_model_name):
    """判断各模型的输入路径"""
    input_dir = "input"
    sep_output_dir = "separation_results"
    karaoke_output_dir = "karaoke_results"
    reverb_output_dir = "deverb_results"
    denoise_output_dir = "denoise_results"

    module_inputs = {
        "sep_vocal_input": None,
        "karaoke_input": None,
        "reverb_input": None,
        "denoise_input": None
    }

    previous_output_dir = input_dir

    if vocal_model_name:
        module_inputs["sep_vocal_input"] = previous_output_dir
        previous_output_dir = sep_output_dir

    if kara_model_name:
        module_inputs["karaoke_input"] = previous_output_dir
        previous_output_dir = karaoke_output_dir

    if reverb_model_name:
        module_inputs["reverb_input"] = previous_output_dir
        previous_output_dir = reverb_output_dir

    if denoise_model_name:
        module_inputs["denoise_input"] = previous_output_dir

    return module_inputs


def select_model():
    """选择使用的模型"""
    models = {}
    print(Fore.BLACK + Style.BRIGHT + "============")
    print("分离人声选项:")
    print("============\n" + Style.RESET_ALL)

    questions = [
        inquirer.List('vocal_model',
                      message=Fore.GREEN + Style.DIM + "请选择需要使用的人声分离模型",
                      choices=[
                          '1.Kim_mel_band_roformer（【推荐】，SDR略微好于另两个且用时减半）',
                          '2.bs-roformer-1297     （ 注：1297的SDR稍高，但有反馈指出可能引入极高频上的噪音，1296则没有）',
                          '3.bs-roformer-1296',
                          '4.不使用'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['vocal_model'] != '4.不使用':
        if answers['vocal_model'] == '1.Kim_mel_band_roformer（【推荐】，SDR略微好于另两个且用时减半）':
            models['vocal_model_name'] = 'MelBandRoformer_kim.ckpt'
        if answers['vocal_model'] == '2.bs-roformer-1297     （ 注：1297的SDR稍高，但有反馈指出可能引入极高频上的噪音，1296则没有）':
            models['vocal_model_name'] = 'model_bs_roformer_ep_317_sdr_12.9755.ckpt'
        if answers['vocal_model'] == '3.bs-roformer-1296':
            models['vocal_model_name'] = 'model_bs_roformer_ep_368_sdr_12.9628.ckpt'
    else:
        models['vocal_model_name'] = False

    print(Fore.BLACK + Style.BRIGHT + "============")
    print("分离和声选项:")
    print("*也可以单独使用来分离带和声的伴奏")
    print("============\n" + Style.RESET_ALL)

    questions = [
        inquirer.List('kara_model',
                      message=Fore.GREEN + Style.DIM + "请选择需要使用的和声分离模型",
                      choices=[
                          '1.mel_band_roformer_karaoke（【激进】，但性能比UVR现有模型都要好非常多）',
                          '2.不使用                   （ 注：如果1剥残了人声，可以考虑禁用该模块而依靠混响模块去和声）'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['kara_model'] != '2.不使用                   （ 注：如果1剥残了人声，可以考虑禁用该模块而依靠混响模块去和声）':
        if answers['kara_model'] == '1.mel_band_roformer_karaoke（【激进】，但性能比UVR现有模型都要好非常多）':
            models['kara_model_name'] = 'mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt'
    else:
        models['kara_model_name'] = False

    print(Fore.BLACK + Style.BRIGHT + "============")
    print("分离混响和声选项:")
    print("*请注意暂无法单独去混响，和声也可能有残留，需要去和声建议同时启用去和声模块")
    print("============\n" + Style.RESET_ALL)

    questions = [
        inquirer.List('reverb_model',
                      message=Fore.GREEN + Style.DIM + "请选择需要使用的混响和声分离模型",
                      choices=[
                          '1.mel_roformer_anvuew_1917   （【推荐】目前SDR得分最高）',
                          '2.mel_roformer_anvuew_la_1880（【推荐】比1保守，若有剥残情况下选用）',
                          '3.bs_roformer_8_384_10       （ 使用了更多数据训练的新bs模型，SDR更高，在和声分离上比mel系的要保守）',
                          '4.bs_roformer_8_256_8        （ 旧的bs模型）',
                          '5.mel_band_roformer_8_256_6  （ 非常激进的去混响，视曲目不同可能会把人声剥残，但更激进也在一些场合有更好的效果）',
                          '6.mel_band_roformer_8_512_12 （ 比5更大的网络带来稍高的SDR的同时消耗3倍以上推理时间）',
                          '7.mel_band_roformer          （ 最初版模型，在去混响和去和声上有不错的平衡）',
                          '8.不使用'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['reverb_model'] != '8.不使用':
        if answers['reverb_model'] == '1.mel_roformer_anvuew_1917   （【推荐】目前SDR得分最高）':
            models['reverb_model_name'] = 'dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt'
        if answers['reverb_model'] == '2.mel_roformer_anvuew_la_1880（【推荐】比1保守，若有剥残情况下选用）':
            models['reverb_model_name'] = 'dereverb_mel_band_roformer_less_aggressive_anvuew_sdr_18.8050.ckpt'
        if answers['reverb_model'] == '3.bs_roformer_8_384_10       （ 使用了更多数据训练的新bs模型，SDR更高，在和声分离上比mel系的要保守）':
            models['reverb_model_name'] = 'deverb_bs_roformer_8_384dim_10depth.ckpt'
        if answers['reverb_model'] == '4.bs_roformer_8_256_8        （ 旧的bs模型）':
            models['reverb_model_name'] = 'deverb_bs_roformer_8_256dim_8depth.ckpt'
        if answers['reverb_model'] == '5.mel_band_roformer_8_256_6  （ 非常激进的去混响，视曲目不同可能会把人声剥残，但更激进也在一些场合有更好的效果）':
            models['reverb_model_name'] = 'deverb_mel_band_roformer_8_256dim_6depth.ckpt'
        if answers['reverb_model'] == '6.mel_band_roformer_8_512_12 （ 比5更大的网络带来稍高的SDR的同时消耗3倍以上推理时间）':
            models['reverb_model_name'] = 'deverb_mel_band_roformer_8_512dim_12depth.ckpt'
        if answers['reverb_model'] == '7.mel_band_roformer          （ 最初版模型，在去混响和去和声上有不错的平衡）':
            models['reverb_model_name'] = 'deverb_mel_band_roformer_ep_27_sdr_10.4567.ckpt'
    else:
        models['reverb_model_name'] = False

    print(Fore.BLACK + Style.BRIGHT + "============")
    print("降噪选项:")
    print("============\n" + Style.RESET_ALL)

    questions = [
        inquirer.List('denoise_model',
                      message=Fore.GREEN + Style.DIM + "请选择需要使用的降噪模型",
                      choices=[
                          '1.使用SDR 27.9959的通常版模型',
                          '2.使用SDR 27.9768的激进版模型',
                          '3.不使用'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['denoise_model'] != '3.不使用':
        if answers['denoise_model'] == '1.使用SDR 27.9959的通常版模型':
            models['denoise_model_name'] = 'denoise_mel_band_roformer_aufr33_sdr_27.9959.ckpt'
        if answers['denoise_model'] == '2.使用SDR 27.9768的激进版模型':
            models['denoise_model_name'] = 'denoise_mel_band_roformer_aufr33_aggr_sdr_27.9768.ckpt'
    else:
        models['denoise_model_name'] = False

    print(Fore.BLACK + Style.BRIGHT + "============")
    print("附加选项:")
    print("============\n" + Style.RESET_ALL)

    questions = [
        inquirer.List('if_fast',
                      message=Fore.GREEN + Style.DIM + "是否使用快速推理模式？",
                      choices=[
                          '1.使用（将以更低的推理参数进行推理，以SDR稍低的代价换来3-4倍的速度提升，适合配置不高或者大批量推理的场合）',
                          '2.不使用'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['if_fast'] != '2.不使用':
        models['if_fast'] = True
    else:
        models['if_fast'] = False

    questions = [
        inquirer.List('if_save_preset',
                      message=Fore.GREEN + Style.DIM + "是否将目前的流程保存为新预设？",
                      choices=[
                          '1.是',
                          '2.否'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['if_save_preset'] == '1.是':
        questions = [
            inquirer.Text(name='preset_name', message=Fore.GREEN + Style.DIM + "请输入预设名称"),
        ]
        answers = inquirer.prompt(questions, theme=CustomTheme())
        models['preset_name'] = answers['preset_name']
        save_presets(models, )
        print(Fore.RED + '[INFO]' + Style.RESET_ALL + f" 已将目前流程保存为: {models['preset_name']}.json")
        print(Fore.RED + '[INFO]' + Style.RESET_ALL + f" 如果你不再需要该预设，直接从presets文件夹中删除即可")
    else:
        models['preset_name'] = default_config['preset_name']
        save_presets(models, )
        print(Fore.RED + '[INFO]' + Style.RESET_ALL + f" 已将目前流程保存为 {default_config['preset_name']}.json")
    return models


def check_inference_menu(**kwargs):
    """打印推理配置清单"""
    module_inputs = determine_module_inputs(kwargs['vocal_model_name'], kwargs['kara_model_name'], kwargs['reverb_model_name'], kwargs['denoise_model_name'])
    print(Fore.BLACK + Style.BRIGHT + "\n============")
    print("推理配置清单")
    print("============\n" + Style.RESET_ALL)

    if kwargs['vocal_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '分离人声：' + Fore.GREEN + '已启用' + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '使用的模型：' + Style.RESET_ALL + Fore.MAGENTA + kwargs['vocal_model_name'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输入目录：' + Style.RESET_ALL + Fore.CYAN + module_inputs['sep_vocal_input'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输出目录：' + Style.RESET_ALL + Fore.CYAN + 'separation_results\n' + Style.RESET_ALL)
    else:
        print(Fore.BLACK + Style.BRIGHT + '分离人声：' + Fore.RED + '已禁用\n' + Style.RESET_ALL)

    if kwargs['kara_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '分离和声：' + Fore.GREEN + '已启用' + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '使用的模型：' + Style.RESET_ALL + Fore.MAGENTA + kwargs['kara_model_name'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输入目录：' + Style.RESET_ALL + Fore.CYAN + module_inputs['karaoke_input'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输出目录：' + Style.RESET_ALL + Fore.CYAN + 'karaoke_results\n' + Style.RESET_ALL)
    else:
        print(Fore.BLACK + Style.BRIGHT + '分离和声：' + Fore.RED + '已禁用\n' + Style.RESET_ALL)

    if kwargs['reverb_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '分离混响和声：' + Fore.GREEN + '已启用' + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '使用的模型：' + Style.RESET_ALL + Fore.MAGENTA + kwargs['reverb_model_name'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输入目录：' + Style.RESET_ALL + Fore.CYAN + module_inputs['reverb_input'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输出目录：' + Style.RESET_ALL + Fore.CYAN + 'deverb_results\n' + Style.RESET_ALL)
    else:
        print(Fore.BLACK + Style.BRIGHT + '分离混响和声：' + Fore.RED + '已禁用\n' + Style.RESET_ALL)

    if kwargs['denoise_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '降噪：' + Fore.GREEN + '已启用' + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '使用的模型：' + Style.RESET_ALL + Fore.MAGENTA + kwargs['denoise_model_name'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输入目录：' + Style.RESET_ALL + Fore.CYAN + module_inputs['denoise_input'] + Style.RESET_ALL)
        print(Fore.BLACK + Style.BRIGHT + '输出目录：' + Style.RESET_ALL + Fore.CYAN + 'denoise_results\n' + Style.RESET_ALL)
    else:
        print(Fore.BLACK + Style.BRIGHT + '降噪：' + Fore.RED + '已禁用\n' + Style.RESET_ALL)

    if kwargs['if_fast']:
        print(Fore.BLACK + Style.BRIGHT + '快速推理模式：' + Fore.GREEN + '已启用\n' + Style.RESET_ALL)
    else:
        print(Fore.BLACK + Style.BRIGHT + '快速推理模式：' + Fore.RED + '已禁用\n' + Style.RESET_ALL)

    check_menu = input("按回车键继续")


def run(**kwargs):
    module_inputs = determine_module_inputs(kwargs['vocal_model_name'], kwargs['kara_model_name'], kwargs['reverb_model_name'], kwargs['denoise_model_name'])
    if kwargs['vocal_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '================开始分离人声================' + Style.RESET_ALL)
        inference_case = inference_base + f" --start_check_point pretrain/{kwargs['vocal_model_name']}" + f' --input_folder {module_inputs["sep_vocal_input"]} --store_dir separation_results --extract_instrumental'
        if kwargs['vocal_model_name'] == 'model_bs_roformer_ep_317_sdr_12.9755.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/model_bs_roformer_ep_317_sdr_12.9755-fast.yaml' + ' --model_type bs_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/model_bs_roformer_ep_317_sdr_12.9755.yaml' + ' --model_type bs_roformer'

        if kwargs['vocal_model_name'] == 'model_bs_roformer_ep_368_sdr_12.9628.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/model_bs_roformer_ep_368_sdr_12.9628-fast.yaml' + ' --model_type bs_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/model_bs_roformer_ep_368_sdr_12.9628.yaml' + ' --model_type bs_roformer'

        if kwargs['vocal_model_name'] == 'MelBandRoformer_kim.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/config_vocals_mel_band_roformer_kim-fast.yaml' + ' --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/config_vocals_mel_band_roformer_kim.yaml' + ' --model_type mel_band_roformer'
        subprocess.run(f'{inference_case}', shell=True)

    if kwargs['kara_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '================开始分离和声================' + Style.RESET_ALL)
        inference_case = inference_base + ' --model_type mel_band_roformer' + f" --start_check_point pretrain/{kwargs['kara_model_name']}" + f' --input_folder {module_inputs["karaoke_input"]} --store_dir karaoke_results --extract_instrumental'
        if kwargs['if_fast']:
            inference_case = inference_case + ' --config_path configs/config_mel_band_roformer_karaoke-fast.yaml'
        else:
            inference_case = inference_case + ' --config_path configs/config_mel_band_roformer_karaoke.yaml'

        subprocess.run(f'{inference_case}', shell=True)

    if kwargs['reverb_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '================开始分离混响和声================' + Style.RESET_ALL)
        inference_case = inference_base + f" --start_check_point pretrain/{kwargs['reverb_model_name']}" + f' --input_folder {module_inputs["reverb_input"]} --store_dir deverb_results --extract_instrumental'
        if kwargs['reverb_model_name'] == 'deverb_mel_band_roformer_ep_27_sdr_10.4567.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/deverb_mel_band_roformer-fast.yaml  --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/deverb_mel_band_roformer.yaml  --model_type mel_band_roformer'

        if kwargs['reverb_model_name'] == 'deverb_bs_roformer_8_384dim_10depth.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/deverb_bs_roformer_8_384dim_10depth-fast.yaml  --model_type bs_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/deverb_bs_roformer_8_384dim_10depth.yaml  --model_type bs_roformer'

        if kwargs['reverb_model_name'] == 'deverb_bs_roformer_8_256dim_8depth.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/deverb_bs_roformer_8_256dim_8depth-fast.yaml  --model_type bs_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/deverb_bs_roformer_8_256dim_8depth.yaml  --model_type bs_roformer'

        if kwargs['reverb_model_name'] == 'deverb_mel_band_roformer_8_256dim_6depth.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/8_256_6_deverb_mel_band_roformer_8_256dim_6depth-fast.yaml  --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/8_256_6_deverb_mel_band_roformer_8_256dim_6depth.yaml  --model_type mel_band_roformer'

        if kwargs['reverb_model_name'] == 'deverb_mel_band_roformer_8_512dim_12depth.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/8_512_12_deverb_mel_band_roformer_8_512dim_12depth-fast.yaml  --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/8_512_12_deverb_mel_band_roformer_8_512dim_12depth.yaml  --model_type mel_band_roformer'

        if kwargs['reverb_model_name'] == 'dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/dereverb_mel_band_roformer_anvuew-fast.yaml  --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/dereverb_mel_band_roformer_anvuew.yaml  --model_type mel_band_roformer'

        if kwargs['reverb_model_name'] == 'dereverb_mel_band_roformer_less_aggressive_anvuew_sdr_18.8050.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/dereverb_mel_band_roformer_anvuew-fast.yaml  --model_type mel_band_roformer'
            else:
                inference_case = inference_case + ' --config_path configs/dereverb_mel_band_roformer_anvuew.yaml  --model_type mel_band_roformer'
        subprocess.run(f'{inference_case}', shell=True)

    if kwargs['denoise_model_name']:
        print(Fore.BLACK + Style.BRIGHT + '================开始降噪================' + Style.RESET_ALL)
        inference_case = inference_base + f" --model_type mel_band_roformer --start_check_point pretrain/{kwargs['denoise_model_name']}" + f' --input_folder {module_inputs["denoise_input"]} --store_dir denoise_results --extract_instrumental'
        if kwargs['denoise_model_name'] == 'denoise_mel_band_roformer_aufr33_sdr_27.9959.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/model_mel_band_roformer_denoise-fast.yaml'
            else:
                inference_case = inference_case + ' --config_path configs/model_mel_band_roformer_denoise.yaml'

        if kwargs['denoise_model_name'] == 'denoise_mel_band_roformer_aufr33_aggr_sdr_27.9768.ckpt':
            if kwargs['if_fast']:
                inference_case = inference_case + ' --config_path configs/model_mel_band_roformer_denoise-fast.yaml'
            else:
                inference_case = inference_case + ' --config_path configs/model_mel_band_roformer_denoise.yaml'
        subprocess.run(f'{inference_case}', shell=True)


def select_preset():
    if not os.path.isdir('presets'):
        os.mkdir('presets')
    questions = [
        inquirer.List('if_use_presets',
                      message=Fore.GREEN + Style.DIM + "是否读取并使用预设的配置文件？",
                      choices=[
                          '1.使用',
                          '2.不使用'
                      ],
                      ),
    ]
    answers = inquirer.prompt(questions, theme=CustomTheme())

    if answers['if_use_presets'] == '1.使用':
        check_config(default_config_path)
        if not os.path.exists('options.json'):
            print(Fore.RED + '[INFO]' + Style.RESET_ALL + f' "options.json" 文件不存在，创建新配置文件...\n')
            write_config('options.json', default_options)
        update_options()
        data = read_config('options.json')
        choices = data.get('choices', [])
        questions = [
            inquirer.List(
                'selected_option',
                message=Fore.GREEN + Style.DIM + "请选择使用的预设",
                choices=choices,
            ),
        ]
        answers = inquirer.prompt(questions, theme=CustomTheme())
        print(Fore.RED + '\n[INFO]' + Style.RESET_ALL + f" 已选择：{answers['selected_option']}.json\n")
        config = read_config('./presets/' + answers['selected_option'] + '.json')
        return config
    else:
        config = select_model()
        return config


def main():
    ascii_art = text2art("MSST", font='block')
    print(ascii_art)
    print('                                                        v1.3版本  by 领航员未鸟')
    print(Fore.RED + '\n[INFO]' + Style.RESET_ALL + ' 请将所有待处理音频放入input文件夹内...\n')

    config = select_preset()
    check_inference_menu(**config)
    run(**config)
    print(Fore.BLACK + Style.BRIGHT + '================处理完成================' + Style.RESET_ALL)


if __name__ == '__main__':
    main()
    play_sound()

