<?php

declare(strict_types=1);

/*
 * This file is part of the Thelia package.
 * http://www.thelia.net
 *
 * (c) OpenStudio <info@thelia.net>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

namespace FlexyBundle\Components\Layouts\FolderContents;

use Symfony\UX\TwigComponent\Attribute\AsTwigComponent;
use Thelia\Api\Service\DataAccess\DataAccessService;

#[AsTwigComponent]
class Base
{
    private const ITEMS_PER_PAGE = 12;

    public array $contents = [];
    public array $pagination = [];

    public function __construct(
        private readonly DataAccessService $dataAccessService,
    ) {
    }

    public function mount(int $folderId, int $page = 1): void
    {
        $response = $this->dataAccessService->resources('/api/front/contents', [
            'contentFolders.folder.id' => $folderId,
            // Sans tri demandé, la collection sort dans l'ordre des clés
            // primaires : la liste d'un dossier ignore alors l'ordre décidé en
            // back-office et s'ouvre sur son contenu le plus ancien.
            'order[position]' => 'asc',
            'itemsPerPage' => self::ITEMS_PER_PAGE,
            'page' => $page,
        ], 'jsonld');

        $this->contents = $response['hydra:member'] ?? [];
        $this->pagination = [
            'totalItems' => $response['hydra:totalItems'] ?? 0,
            'itemsPerPage' => self::ITEMS_PER_PAGE,
            'currentPage' => $page,
        ];
    }
}
