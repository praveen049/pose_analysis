import commands
import sys

def getFPS(filename):

    status, output = commands.getstatusoutput("ffmpeg -i "+filename+" -vcodec copy -f rawvideo -y /dev/null 2>&1 | tr ^M '\n' | grep -i 'fps'")
    print(status)
    print(output)
	
    if status != 0:
        return 0
    
    lines = output.split('\n')

    entrys = lines[0].split(', ')
    
    fps = 0;
    frame = 0;
    
    for entry in entrys:
        print(entry)
        posFPS = entry.find('fps')
        print(posFPS)
        if(posFPS > 0):
            fpsStr = entry.split(' ')[0]
            print(fpsStr)
            fps = float(fpsStr)
            break

    
    entrys = lines[2].split(' ')
    frame = float(entrys[1])
    '''
    for entry in entrys:
        print(entry)
        posFrame = entry.find('frame')
        print(posFrame)
        if posFrame > 0:
            frameStr = entry.split(' ')[1]
            frame = float(frameStr)
            break
    '''			
    return fps, frame   


fps,frame = getFPS(sys.argv[1])
print(fps)
print(frame)

