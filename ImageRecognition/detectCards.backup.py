import cv2
import numpy as np
import matplotlib.pyplot as plt

from turnGen.objects.Card import Card
from turnGen.objects.Gameboard import Gameboard
from turnGen.objects.Pile import Pile
import turnGen.BoardConverter as BoardConverter


# Frederik Koefoed s195463
# Lasse Strunge s195486
# Mark Mortensen s174881
# Mikkel Danielsen s183913
# Muhammad Talha s195475
# Volkan Isik s180103
class Detector:
    def detectSolitaire(self,path):
        # Load Yolo
        net = cv2.dnn.readNet("/home/cdio/syvkabale/syvkabaleBE/ImageRecognition/ModelFiles/last.weights", "/home/cdio/syvkabale/syvkabaleBE/ImageRecognition/ModelFiles/yolo-obj.cfg")
        classes = []
        with open("/home/cdio/syvkabale/syvkabaleBE/ImageRecognition/ModelFiles/card.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        # Loading image
        img = cv2.imread(path)
        img = cv2.resize(img, None, fx=0.4, fy=0.4)
        height, width, channels = img.shape

        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        print(indexes)
        font = cv2.FONT_HERSHEY_PLAIN

        cards = []
        diff = 75

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 3, color, 3)
                cards.append((label, x, y, w, h))

                # if len(cards) > 1:
                for j in range(len(cards)):
                    if cards[j][0] == label and cards[j][0] != "backside":
                        if cards[j][1] < x:
                            cards.pop()
                            break
                        elif x < cards[j][1]:
                            cards[j] = cards.pop()
                            break

                        if cards[j][2] < y:
                            cards.pop()
                            break

        print("Cards:")
        print(cards)

        # take second element for sort
        def takeSecond(elem):
            return elem[1]

        cards.sort(key=takeSecond)

        pilecoords = []
        deck = []
        finspaces = []

        gnswidth = 0
        gnsheight = 0
        totalwidth = 0
        totalheight = 0
        cardcount = 0
        for i in range(len(cards)):
            if cards[i][0] != 'backside':
                totalwidth += cards[i][3]
                totalheight += cards[i][4]
                cardcount = cardcount + 1

        gnswidth = int(totalwidth / cardcount)
        gnsheight = int(totalheight / cardcount)

        deckXYmin = (0, 0)
        deckXYmax = (int(width * 1 / 3), int(height * 1 / 3))
        finspacesXYmin = ((int(width * (1 / 3))) + 100, 0)
        finspacesXYmax = (width, int(height * (1 / 3)))

        length = len(cards)
        count = 0
        while count < length:
            if cards[count][1] < deckXYmax[0] and cards[count][2] < deckXYmax[1]:
                deck.append(cards[count])
                cards.remove(cards[count])
                length = length - 1
                count = count - 1
            if cards[count][1] > finspacesXYmin[0] and cards[count][2] < finspacesXYmax[1]:
                finspaces.append(cards[count])
                cards.remove(cards[count])
                length = length - 1
                count = count - 1
            count = count + 1

        deck.sort(key=takeSecond)
        print("Deck:")
        print(deck)

        finspaces.sort(key=takeSecond)
        print("Finspaces:")
        print(finspaces)

        xcoord = 0
        offset = 2 * gnswidth  # ret værdien efter størrelsen af billedet
        exist = True

        for i in range(len(cards)):
            if (xcoord < cards[i][1]):
                xcoord = cards[i][1]
                if len(pilecoords) == 0:
                    pilecoords.append(xcoord)

                for j in range(len(pilecoords)):
                    if pilecoords[j] + offset < xcoord:
                        exist = False
                    else:
                        exist = True

                if not exist:
                    pilecoords.append(xcoord)

                exist = True

        print("Piles:")
        print(len(pilecoords))  # antal piles
        print(pilecoords)

        if len(pilecoords) > 7:
            iarrangepilecoords = 0
            lengtharrangepilecoords = len(pilecoords) - 1
            while iarrangepilecoords < lengtharrangepilecoords:
                if pilecoords[iarrangepilecoords] > gnswidth:
                    pilecomp = pilecoords[iarrangepilecoords]
                    if pilecomp + gnswidth * 7.5 > pilecoords[iarrangepilecoords + 1]:
                        pilecoords.remove(pilecoords[iarrangepilecoords + 1])
                        iarrangepilecoords = iarrangepilecoords - 1
                        lengtharrangepilecoords = lengtharrangepilecoords - 1
                else:
                    pilecoords.remove(pilecoords[iarrangepilecoords])
                    iarrangepilecoords = iarrangepilecoords - 1
                    lengtharrangepilecoords = lengtharrangepilecoords - 1
                iarrangepilecoords = iarrangepilecoords + 1

        print("Piles:")
        print(len(pilecoords))  # antal piles
        print(pilecoords)

        def takeThird(elem):
            return elem[2]

        cards.sort(key=takeThird)

        piles = []
        for i in range(len(pilecoords)):
            rightOff = pilecoords[i] + offset
            leftOff = pilecoords[i] - offset
            pile = []
            for j in range(len(cards)):
                if (cards[j][1] <= rightOff) and (cards[j][1] >= leftOff):
                    pile.append(cards[j])
            piles.append(pile)

        print("Cards in Piles:")
        print(piles)
        print(gnswidth)

        # converters for imgRecon classes to Card objects
        typeConverter = {"s": 0,
                         "h": 1,
                         "c": 2,
                         "d": 3}

        valueConverter = {"A": 1,
                          "2": 2,
                          "3": 3,
                          "4": 4,
                          "5": 5,
                          "6": 6,
                          "7": 7,
                          "8": 8,
                          "9": 9,
                          "1": 10,
                          "J": 11,
                          "Q": 12,
                          "K": 13}

        gameboard = Gameboard(0)

        for pile in piles:
            # initial pile
            hiddenCards = []
            shownCards = []
            for card in pile:
                if card[0] == "backside":
                    # if cards in pile is a backside, we add it to the hidden cards
                    # value 14 for app to show hidden card
                    hiddenCards.append(Card(0, 14))
                else:
                    # adding found card to pile
                    newCard = Card(typeConverter[card[0][-1]], valueConverter[card[0][0]])
                    shownCards.append(newCard)

            gameboard.spaces.append(Pile(shownCards, hiddenCards))

        if len(deck) != 0:
            deckCardClass = deck[0][0]  # finds class for card shown from deck
            # creates Card-objekt with correct values
            gameboard.deck.append(Card(typeConverter[deckCardClass[1]], valueConverter[deckCardClass[0]]))
            # makes deckpointer point correctly at first index
            gameboard.deckPointer = 0
        else:
            # no card on deck so deckpointer points at nothing
            gameboard.deckPointer = -1

        for card in finspaces:
            # creates Card-object
            newCard = Card(typeConverter[card[0][1]], valueConverter[card[0][0]])

            # adding the card to the correct pile
            gameboard.finSpaces[gameboard.finSpaceConverter[newCard.type]].append(newCard)

        # boardConverter adds all missing cards not seen under the found card
        BoardConverter.convertBoard(gameboard)

        # gameboard is now the Gameboard-object of the found solitaire

        # should return gameboard and be converted in app.py
        # json = gameboardEncoder(gameboard)
        # print(json)

        # plt.imshow(img)
        # plt.show()
        # cv2.imshow("cards", img)
        # cv2.waitKey(60)
        # cv2.destroyAllWindows()
        return gameboard
