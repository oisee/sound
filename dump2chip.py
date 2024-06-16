import argparse
import json

RAW_REGS = 16
REG_NUM = 14

def read_aydump_file(filename):
    frames = []
    with open(filename, 'r') as file:
        for line in file:
            frame = []
            for value in line.strip().split('\t'):
                if value == '_':
                    frame.append(None)
                else:
                    frame.append(int(value))
            frames.append(frame)
    return frames

def generate_mask(mixer, tone_mask, noise_mask, envelope_mask):
    mask = []
    if noise_mask & mixer:
        mask.append('n')
    else:
        mask.append('_')
    if envelope_mask & mixer:
        mask.append('e')
    else:
        mask.append('_')
    if tone_mask & mixer:
        mask.append('t')
    else:
        mask.append('_')
    return ''.join(mask)

def frame_to_dict(frame):
    result = {}

    # Tone periods
    if frame[0] is not None or frame[1] is not None:
        result['At'] = ((frame[1] if frame[1] is not None else 0) << 8) | (frame[0] if frame[0] is not None else 0)
    if frame[2] is not None or frame[3] is not None:
        result['Bt'] = ((frame[3] if frame[3] is not None else 0) << 8) | (frame[2] if frame[2] is not None else 0)
    if frame[4] is not None or frame[5] is not None:
        result['Ct'] = ((frame[5] if frame[5] is not None else 0) << 8) | (frame[4] if frame[4] is not None else 0)
    
    # Volumes
    if frame[8] is not None:
        result['Av'] = frame[8] & 0x0f
    if frame[9] is not None:
        result['Bv'] = frame[9] & 0x0f
    if frame[10] is not None:
        result['Cv'] = frame[10] & 0x0f
    
    # Noise period
    if frame[6] is not None:
        result['N'] = frame[6] & 0x1f
    
    # Envelope period and shape
    if frame[11] is not None or frame[12] is not None:
        result['Ep'] = ((frame[12] if frame[12] is not None else 0) << 8) | (frame[11] if frame[11] is not None else 0)
    if frame[13] is not None:
        result['Es'] = frame[13] & 0xff
    
    # Mixer control
    if frame[7] is not None:
        mixer = frame[7]
        result['Am'] = generate_mask(mixer, 0x01, 0x08, 0x10)
        result['Bm'] = generate_mask(mixer, 0x02, 0x10, 0x20)
        result['Cm'] = generate_mask(mixer, 0x04, 0x20, 0x40)
    
    return result

def convert_to_jsonl(frames, output_filename):
    with open(output_filename, 'w') as file:
        for frame in frames:
            frame_dict = frame_to_dict(frame)
            if not frame_dict:
                frame_dict = {}
            file.write(json.dumps(frame_dict, sort_keys=True) + '\n')

def main(input_filename, output_filename):
    frames = read_aydump_file(input_filename)
    convert_to_jsonl(frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert AY register dump to JSONL format.')
    parser.add_argument('input_filename', nargs='?', default='sync.psg.aydump', help='The input AY register dump file (default: sync.psg.aydump)')
    parser.add_argument('output_filename', nargs='?', help='The output JSONL file (default: input_filename.jsonl)')
    args = parser.parse_args()
    
    input_filename = args.input_filename
    output_filename = args.output_filename if args.output_filename else input_filename + '.jsonl'
    
    main(input_filename, output_filename)
