SetDirectory[DirectoryName[$InputFileName]];

hEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 4, 1 \[UndirectedEdge] 5, 2 \[UndirectedEdge] 3, 2 \[UndirectedEdge] 4, 2 \[UndirectedEdge] 5, 3 \[UndirectedEdge] 4, 3 \[UndirectedEdge] 5, 4 \[UndirectedEdge] 5};
gEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 4, 1 \[UndirectedEdge] 5, 1 \[UndirectedEdge] 6, 1 \[UndirectedEdge] 9, 1 \[UndirectedEdge] 10, 1 \[UndirectedEdge] 14, 1 \[UndirectedEdge] 22, 1 \[UndirectedEdge] 24, 1 \[UndirectedEdge] 28, 1 \[UndirectedEdge] 29, 1 \[UndirectedEdge] 30, 1 \[UndirectedEdge] 45, 1 \[UndirectedEdge] 46, 3 \[UndirectedEdge] 4, 4 \[UndirectedEdge] 5, 4 \[UndirectedEdge] 6, 4 \[UndirectedEdge] 8, 4 \[UndirectedEdge] 10, 4 \[UndirectedEdge] 11, 4 \[UndirectedEdge] 12, 4 \[UndirectedEdge] 13, 4 \[UndirectedEdge] 16, 4 \[UndirectedEdge] 18, 4 \[UndirectedEdge] 19, 4 \[UndirectedEdge] 21, 4 \[UndirectedEdge] 29, 4 \[UndirectedEdge] 34, 4 \[UndirectedEdge] 42, 4 \[UndirectedEdge] 45, 4 \[UndirectedEdge] 50, 5 \[UndirectedEdge] 7, 5 \[UndirectedEdge] 9, 5 \[UndirectedEdge] 11, 5 \[UndirectedEdge] 21, 5 \[UndirectedEdge] 23, 5 \[UndirectedEdge] 24, 5 \[UndirectedEdge] 33, 5 \[UndirectedEdge] 34, 5 \[UndirectedEdge] 35, 5 \[UndirectedEdge] 37, 5 \[UndirectedEdge] 39, 5 \[UndirectedEdge] 49, 6 \[UndirectedEdge] 7, 6 \[UndirectedEdge] 47, 7 \[UndirectedEdge] 8, 7 \[UndirectedEdge] 13, 7 \[UndirectedEdge] 15, 7 \[UndirectedEdge] 27, 7 \[UndirectedEdge] 31, 7 \[UndirectedEdge] 40, 8 \[UndirectedEdge] 17, 8 \[UndirectedEdge] 33, 8 \[UndirectedEdge] 40, 8 \[UndirectedEdge] 47, 8 \[UndirectedEdge] 48, 9 \[UndirectedEdge] 17, 9 \[UndirectedEdge] 19, 9 \[UndirectedEdge] 20, 9 \[UndirectedEdge] 35, 10 \[UndirectedEdge] 15, 10 \[UndirectedEdge] 26, 10 \[UndirectedEdge] 30, 10 \[UndirectedEdge] 37, 10 \[UndirectedEdge] 44, 11 \[UndirectedEdge] 12, 11 \[UndirectedEdge] 16, 11 \[UndirectedEdge] 38, 11 \[UndirectedEdge] 39, 12 \[UndirectedEdge] 18, 12 \[UndirectedEdge] 49, 13 \[UndirectedEdge] 14, 13 \[UndirectedEdge] 26, 13 \[UndirectedEdge] 27, 14 \[UndirectedEdge] 43, 14 \[UndirectedEdge] 44, 15 \[UndirectedEdge] 23, 15 \[UndirectedEdge] 41, 18 \[UndirectedEdge] 25, 19 \[UndirectedEdge] 20, 19 \[UndirectedEdge] 32, 19 \[UndirectedEdge] 46, 19 \[UndirectedEdge] 48, 20 \[UndirectedEdge] 22, 20 \[UndirectedEdge] 36, 21 \[UndirectedEdge] 36, 21 \[UndirectedEdge] 43, 22 \[UndirectedEdge] 25, 25 \[UndirectedEdge] 28, 27 \[UndirectedEdge] 41, 28 \[UndirectedEdge] 31, 28 \[UndirectedEdge] 32, 37 \[UndirectedEdge] 38, 39 \[UndirectedEdge] 42, 47 \[UndirectedEdge] 50};
vertexMapping = <|1 -> 1, 2 -> 4, 3 -> 5, 4 -> 6, 5 -> 8|>;
edgeMapping = <|1 -> {1 \[UndirectedEdge] 3, 3 \[UndirectedEdge] 4}, 2 -> {1 \[UndirectedEdge] 24, 5 \[UndirectedEdge] 24}, 3 -> {1 \[UndirectedEdge] 4, 4 \[UndirectedEdge] 50, 47 \[UndirectedEdge] 50, 6 \[UndirectedEdge] 47}, 4 -> {1 \[UndirectedEdge] 9, 9 \[UndirectedEdge] 17, 8 \[UndirectedEdge] 17}, 5 -> {4 \[UndirectedEdge] 11, 5 \[UndirectedEdge] 11}, 6 -> {4 \[UndirectedEdge] 13, 7 \[UndirectedEdge] 13, 6 \[UndirectedEdge] 7}, 7 -> {4 \[UndirectedEdge] 5, 5 \[UndirectedEdge] 33, 8 \[UndirectedEdge] 33}, 8 -> {1 \[UndirectedEdge] 5, 1 \[UndirectedEdge] 6}, 9 -> {5 \[UndirectedEdge] 7, 7 \[UndirectedEdge] 8}, 10 -> {4 \[UndirectedEdge] 6, 4 \[UndirectedEdge] 8}|>;

edgeColorList = ColorData[97] /@ Range[Length[hEdges]];
hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];
gImmersedStyleRules = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.6]]],
    {i, Length[hEdges]}
  ]
];
gBackgroundStyleRules = Thread[
  Complement[EdgeList[Graph[Range[50], gEdges]], Flatten[Values[edgeMapping]]] ->
    Directive[GrayLevel[0.72], Opacity[0.24], AbsoluteThickness[0.7]]
];
branchVertexStyleRules = Thread[Values[vertexMapping] -> Directive[Black, PointSize[0.018]]];

hPlot = Graph[
  Range[5],
  hEdges,
  VertexLabels -> Placed["Name", Center],
  GraphLayout -> "CircularEmbedding",
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 260,
  PlotLabel -> Style["H = K5", 14, FontFamily -> "Arial"]
];

gPlot = Graph[
  Range[50],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRules],
  VertexStyle -> branchVertexStyleRules,
  VertexSize -> 0.11,
  ImageSize -> 540,
  PlotLabel -> Style["G = BA(50, 2), seed 0", 14, FontFamily -> "Arial"]
];

mappingPanel = Pane[
  Framed[
    Column[{
    Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
    vertexMapping,
    Spacer[8],
    Style["Edge mapping: each K5 color matches its immersed path", Bold, 12, FontFamily -> "Arial"],
    edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {820, 190},
  Scrollbars -> False
];

figure = Grid[
  {{hPlot, gPlot}, {SpanFromLeft, mappingPanel}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];

Export["k5_ba_native_colored.pdf", figure];
Export["k5_ba_native_colored.png", figure, ImageResolution -> 300];
Export["k5_ba_h_native_colored.pdf", hPlot];
Export["k5_ba_g_native_colored.pdf", gPlot];

Print["Exported native Mathematica colored figures."];
