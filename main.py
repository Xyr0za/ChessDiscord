import discord
from discord.ext import commands
import chess

BOT_TOKEN = # Token Here
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

pieceDict = {
    # White
    "R": "❎",
    "N": "🐴",
    "B": "✝",
    "Q": ":dvd:",
    "K": "👑",
    "P": "🌕",
    # Black
    "r": "🇽",
    "n": "🐪",
    "b": "☦",
    "q": ":cd:",
    "k": ":gem:",
    "p": "🌑"
}


def fen_to_board(fen, pieces, t):
    num = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:"]
    rows = fen.split("/")[0:8]
    if t[0].lower() == "b":
        rows.reverse()
        rows = [i[::-1] for i in rows]

    else:
        num.reverse()
    out = []
    C = 1

    for r, i in enumerate(rows):
        currentRow = [num[r]]
        for j, v in enumerate(i):  # [r,n,b,q,k,b,n,r]

            if v.isdigit():  # [4,N,3]
                for o in range(0, int(v)):
                    if C % 2 == 0:
                        currentRow.append("🟫")
                    else:
                        currentRow.append("⬜")
                    C += 1

            if v in pieceDict:
                currentRow.append(pieceDict.get(v))
                C += 1
        out.append(''.join(currentRow))
        C -= 1

    if t[0].lower() != "b":
        out.append(":red_square:"
               ":regional_indicator_a::regional_indicator_b::regional_indicator_c::regional_indicator_d:"
               ":regional_indicator_e::regional_indicator_f::regional_indicator_g::regional_indicator_h:")
    else:
        out.append(":red_square:"
                   ":regional_indicator_h::regional_indicator_g::regional_indicator_f::regional_indicator_e:"
                   ":regional_indicator_d::regional_indicator_c::regional_indicator_b::regional_indicator_a:")

    return out


def embed_setup(val):
    display = "\n".join(fen_to_board(val[0], pieceDict, val[1]))
    move = "White" if val[1] == "w" else "Black"

    castleRights = val[2]

    moveNum = val[-1]
    halfMoves = val[-2]
    embed = discord.Embed(title=f"#{halfMoves} - #{moveNum} ", description=display,
                          colour=discord.Colour.light_embed() if move == "White" else discord.Colour.darker_gray())
    embed.add_field(name="Castle", value=castleRights)
    if val[3] != "-":
        embed.add_field(name="En Passant", value=val[3])
    return embed, move


def piece_display(pieces):

    p = []

    for key in pieces:
        p.append(f"{pieces.get(key)} - {key}")

    white, black = p[0:6], p[6:]

    return white, black


board = chess.Board()

latest = None


@bot.command()
async def move(ctx, arg):  # ctx, move
    global latest, board
    await ctx.message.delete()

    iMove = chess.Move.from_uci(arg)
    if iMove in board.legal_moves:
        board.push(iMove)
    else:
      return

    embed, moveT = embed_setup(board.fen().split(" "))

    try:
        latest = await latest.edit(embed=embed)
        await latest.edit(content=f"__**{moveT}'s move**__")
    except AttributeError:
        latest = await ctx.send(embed=embed)

    if board.is_checkmate():
        await latest.edit(content=f"__**Checkmate**__")


@bot.command()
async def show(ctx):
    global latest, board
    await ctx.message.delete()

    board = board

    embed, move = embed_setup(board.fen().split(" "))
    try:
        latest = await latest.edit(embed=embed)
        await latest.edit(content=f"__**{move}'s move**__")
    except AttributeError:
        latest = await ctx.send(f"__**{move}'s move**__", embed=embed)


@bot.command()
async def gameReset(ctx):
    global board, latest
    await ctx.message.delete()

    board = chess.Board()
    embed, move = embed_setup(board.fen().split(" "))
    try:
        latest = await latest.edit(embed=embed)
        await latest.edit(content=f"__**{move}'s move**__")
    except AttributeError:
        latest = await ctx.send(f"__**{move}'s move**__", embed=embed)


@bot.command()
async def loadFen(ctx, *args):
    global board, latest
    await ctx.message.delete()

    board = board.set_fen(" ".join(args))
    embed, move = embed_setup(board.fen().split(" "))
    try:
        latest = await latest.edit(embed=embed)
        await latest.edit(content=f"__**{move}'s move**__")
    except AttributeError:
        latest = await ctx.send(embed=embed)


@bot.command()
async def displayPieces(ctx):
    global board, latest
    await ctx.message.delete()

    default = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    embed, move = embed_setup(board.fen().split(" "))
    embed.remove_field(index=0)
    embed.colour = discord.Colour.dark_gold()

    white, black = piece_display(pieceDict)

    embed.add_field(name="White", value="\n".join(white))
    embed.add_field(name="Black", value="\n".join(black))
    try:
        latest = await latest.edit(embed=embed)
    except AttributeError:
        latest = await ctx.send("__**Pieces**__", embed=embed)


@bot.command()
async def fenDisplay(ctx, *args):
    global latest
    await ctx.message.delete()

    embed, move = embed_setup(args)
    try:
        latest = await latest.edit(embed=embed)
        await latest.edit(content=f"__**{move}'s move**__")
    except AttributeError:
        latest = await ctx.send(f"__**{move}'s move**__", embed=embed)

bot.run(BOT_TOKEN)
