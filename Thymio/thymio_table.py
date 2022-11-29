from controller.behaviors.tagger import Tagger


if __name__ == '__main__':
    try:
        tagger = Tagger()
        tagger.run(steps=1800)

    except Exception as e:
        tagger.kill()
